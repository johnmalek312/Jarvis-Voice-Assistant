from llama_index.readers.docstring_walker import DocstringWalker
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.llms.openai import OpenAI

from generation_workflow.workflow import FunctionCallingAgent


from typing import Dict, Any
from tool_registry import TOOL_REGISTRY


import scripts # needed
from config import *

class LlamaIndexHandler:
    def __init__(self, directory_path: str, api_key: str):
        walker = DocstringWalker()
        documents = walker.load_data(directory_path)
        vector_store = SimpleVectorStore()
        self.embed_model = OpenAIEmbedding(api_key=api_key)
        self.index = VectorStoreIndex.from_documents(documents=documents, vector_store=vector_store, embed_model=self.embed_model)
        self.retriever = self.index.as_retriever(similarity_top_k=3)

    def retrieve_nodes(self, query: str):
        """Retrieve relevant documents using the retriever."""
        return self.retriever.retrieve(query)


class LLMResponseGenerator:
    def __init__(self, api_key, model_name, sys_prompt, n_message_history=3, directory_path="scripts", trace = False):
        if trace:
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
        self.llm = OpenAI(api_key=api_key, model=model_name)
        self.tools = TOOL_REGISTRY
        self.index_handler = LlamaIndexHandler(directory_path=directory_path, api_key=api_key)
        self.agent_flow = FunctionCallingAgent(
            llm=self.llm,
            tools=self.tools,
            system_prompt=sys_prompt,
            n_message_history=n_message_history,
            index_handler=self.index_handler,
            timeout=MODEL_CONFIG['timeout']
        )

    async def get_response(self, input_text: str) -> Dict[str, Any]:
        """Generates a response for the given input text using the LLM model. This passes the input into LlamaIndex workflow."""
        try:
            result = await self.agent_flow.run(input=input_text)
            return result["response"]
        except Exception as e:
            print(f"Error generating response: {e}")
            return {"error": str(e)}

    async def reset_messages(self):
        """Clears the assistant's message history. Call this method to clear the chat history, reset the assistant's memory, or initiate a new conversation."""
        self.agent_flow.memory.from_defaults(llm=self.llm)