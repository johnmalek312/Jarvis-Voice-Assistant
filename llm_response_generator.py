import llama_index.core.workflow.errors
import tiktoken
from llama_index.core.callbacks import TokenCountingHandler, CallbackManager
from llama_index.readers.docstring_walker import DocstringWalker
from llama_index.core import VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.core.vector_stores import SimpleVectorStore

import config
import prompts
from workflow.workflow import FunctionCallingAgent
from tool_registry import TOOL_REGISTRY

from config import *

# Add Phoenix API Key for tracing
import os
from helpers import utils
os.environ["OPENAI_API_KEY"] = APIConfig.OPENAI

from logger import app_logger as logging

from scripts import data_manager
from helpers import llamaindex_helper # required monkey patching

#region config
if config.EmbeddingModel == "openai":
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding(api_key=APIConfig.OPENAI, model=OpenaiEmbeddingConfig.MODEL, embed_batch_size=OpenaiEmbeddingConfig.EMBED_BATCH_SIZE)
elif config.EmbeddingModel == "huggingface":
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    embed_model = HuggingFaceEmbedding(HuggingFaceEmbeddingConfig.MODEL)

if config.LLM_provider == "openai":
    from llama_index.llms.openai import OpenAI
    llm = OpenAI(api_key=APIConfig.OPENAI, model=OpenAILLMConfig.LLM_MODEL, temperature=OpenAILLMConfig.LLM_TEMPERATURE)
elif config.LLM_provider == "gemini":
    from llama_index.llms.gemini import Gemini
    llm = Gemini(api_key=APIConfig.GEMINI, model=GeminiLLMConfig.LLM_MODEL, temperature=GeminiLLMConfig.LLM_TEMPERATURE)
#endregion config


class LlamaIndexHandler:
    def __init__(self, directory_path: str, api_key: str, callback_manager = None):
        walker = DocstringWalker()
        documents = walker.load_data(directory_path)
        self.embed_model = embed_model
        hash_file = os.path.join(CACHE_DIRECTORY, "index/doc.hash") # cache directory
        hash_meta = f"{embed_model.model_name}" # hash metadata
        self.hash = None
        if os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                self.hash = f.read()
        if utils.compute_documents_hash(documents, hash_meta) == self.hash:
            logging.info("Loading index from cache.")
            storage_context = StorageContext.from_defaults(persist_dir=CACHE_DIRECTORY + "/index")
            self.index = load_index_from_storage(storage_context=storage_context, embed_model=self.embed_model, callback_manager=callback_manager)
        else:
            logging.info("Rebuilding index.")
            vector_store = SimpleVectorStore()
            self.index = VectorStoreIndex.from_documents(documents=documents, vector_store=vector_store,
                                                         embed_model=self.embed_model,
                                                         callback_manager=callback_manager)
            self.index.storage_context.persist(persist_dir=CACHE_DIRECTORY + "/index")
            with open(hash_file, "w") as f:
                f.write(utils.compute_documents_hash(documents, hash_meta))
        self.retriever = self.index.as_retriever(similarity_top_k=Top_K_Retriever)
    def retrieve_nodes(self, query: str):
        """Retrieve relevant documents using the retriever."""
        nodes = self.retriever.retrieve(query)
        logging.info(f"Retrieved {len(nodes)} nodes.")
        return nodes




class LLMResponseGenerator:
    def __init__(self, api_key=APIConfig.OPENAI, sys_prompt=prompts.gemini_prompt, n_message_history=config.MAX_MESSAGE_HISTORY, directory_path="scripts", trace = trace):
        if trace:
            logging.info("Initializing LlamaIndex Tracing...")
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={APIConfig.PHOENIX}"
            from opentelemetry.sdk import trace as trace_sdk
            from opentelemetry.sdk.trace.export import SimpleSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter as HTTPSpanExporter,
            )
            from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
            # Add Phoenix exporter
            span_phoenix_processor = SimpleSpanProcessor(
                HTTPSpanExporter(endpoint="https://app.phoenix.arize.com/v1/traces")
            )

            # Add span processor to tracer
            tracer_provider = trace_sdk.TracerProvider()
            tracer_provider.add_span_processor(span_phoenix_processor)

            # Instrument LlamaIndex
            LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

        self.workflow_handler = None


        self.llm = llm
        try:
            tokenizer = tiktoken.encoding_for_model(self.llm.model).encode
        except:
            tokenizer = tiktoken.encoding_for_model("gpt-4o-mini").encode
        self.token_counter = TokenCountingHandler( # set up token counter
            tokenizer=tokenizer,
        )
        self.callback_manager = CallbackManager([self.token_counter]) # set up callback manager for token counter
        data_manager.DataManager.token_counter = self.token_counter # set the token counter for data manager to use in scripts
        data_manager.DataManager.llm = self
        self.tools = TOOL_REGISTRY
        self.index_handler = None
        if Top_K_Retriever != -1:
            self.index_handler = LlamaIndexHandler(directory_path=directory_path, api_key=api_key, callback_manager=self.callback_manager)

        self.agent_flow = FunctionCallingAgent(
            llm=self.llm,
            tools=self.tools,
            system_prompt=sys_prompt,
            n_message_history=n_message_history,
            index_handler=self.index_handler,
            timeout=timeout,
            callback_manager=self.callback_manager
        )


    async def get_response(self, input_text: str) -> str | None:
        """Generates a response for the given input text using the LLM model. This passes the input into LlamaIndex workflow."""
        try:
            self.workflow_handler = self.agent_flow.run(input=input_text)
            result = await self.workflow_handler
            return result["response"]
        except llama_index.core.workflow.errors.WorkflowCancelledByUser:
            return None
        # except Exception as e:
        #     print(f"Error generating response: {e}")
        #     return "error" + str(e)

    async def reset_messages(self):
        """Clears the assistant's message history. Call this method to clear the chat history, reset the assistant's memory, or initiate a new conversation."""
        self.agent_flow.reset()


