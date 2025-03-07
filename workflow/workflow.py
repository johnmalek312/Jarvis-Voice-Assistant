from typing import Any
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step
from llama_index.llms.openai import OpenAI



from tool_registry import TOOL_REGISTRY
from .response_event import InputEvent, ToolCallEvent, ThinkingEvent
from logger import app_logger as logging
from config import Top_K_Retriever, thinking_mode

from prompts import planning_template, execute_plan_prompt, system_planning

class FunctionCallingAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: FunctionCallingLLM | None = None,
        system_prompt: str = "",
        n_message_history: int = 3,
        index_handler = None,
        tools,
        callback_manager = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm or OpenAI()
        assert self.llm.metadata.is_function_calling_model

        self.sys_message = ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
        if callback_manager:
            self.llm.callback_manager = callback_manager # set the callback manager for llm
        self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[self.sys_message] if self.sys_message.content else None)
        self.sources = []
        self.n_message_history = n_message_history * (thinking_mode * 2 + 1)


        self.index_handler = index_handler # used to retrieve relevant nodes
        self.current_tools: list[FunctionTool] = [] # the list of tools passed to the LLM
        self.tools: list[dict] = tools # the list of all available tools, those are filtered (query retrieval)
    def reset(self):
        self.memory = ChatMemoryBuffer.from_defaults(llm=self.llm, chat_history=[self.sys_message] if self.sys_message.content else None)
        self.sources = []
        self.current_tools = []
    @step
    async def prepare_chat_history(self, ev: StartEvent) -> InputEvent | StopEvent | ThinkingEvent:
        """Prepare chat history for the LLM."""
        # clear sources
        self.sources = []
        last_x_messages = self.memory.get_last_messages(n=self.n_message_history)
        self.memory = ChatMemoryBuffer.from_defaults(llm=self.llm, chat_history=last_x_messages)
        # get user input
        user_input = ev.input
        if thinking_mode:
            plan_message = ChatMessage(role="user", content=system_planning)
            self.memory.put(plan_message)
            return ThinkingEvent(input=self.memory.get(), message=user_input)
        user_msg = ChatMessage(role="user", content=user_input)
        self.memory.put(user_msg)
        # get chat history
        chat_history = self.memory.get()
        return InputEvent(input=chat_history, message=user_input)
    
    @step
    async def handle_thinking(self, ev: ThinkingEvent) -> InputEvent:
        """Handle the thinking event."""
        query = ev.message
        if Top_K_Retriever == -1:
            self.current_tools = [list(d.values())[0] for d in TOOL_REGISTRY]
        elif query:
            # retrieve relevant nodes
            nodes = self.index_handler.retrieve_nodes(query)
            self.current_tools = FunctionCallingAgent.get_tools_from_nodes(nodes=nodes) or []
        chat_history = ev.input
        # I want to set context_str to self.current_tools[x].metadata.description where all tools are joined by double \n
        message = planning_template.format(context_str="\n\n".join([tool.metadata.description for tool in self.current_tools]), query_str=query)
        self.memory.put(ChatMessage(role="user", content=message))
        chat_history.append(self.memory.get()[-1])
        response = await self.llm.achat(
            messages=chat_history
        )
        logging.info("Thinking response: " + str(response.message) + "\n\n\n")
        self.memory.put(response.message)
        self.memory.put(ChatMessage(role="user", content=execute_plan_prompt))
        return InputEvent(input=self.memory.get())

    @step
    async def handle_llm_input(
        self, ev: InputEvent
    ) -> ToolCallEvent | StopEvent:
        """Handle input to the LLM and retreive the most relevant tools using RAG."""
        message = ev.message
        if Top_K_Retriever == -1:
            self.current_tools = [list(d.values())[0] for d in TOOL_REGISTRY]
        elif message:
            # retrieve relevant nodes
            nodes = self.index_handler.retrieve_nodes(message)
            self.current_tools = FunctionCallingAgent.get_tools_from_nodes(nodes=nodes) or []
            ### make the current tools be the tools where key is "static" from self.tools list of key value pairs
        chat_history = ev.input
        response = await self.llm.achat_with_tools(
            tools=self.current_tools, chat_history=chat_history, allow_parallel_tool_calls=True, verbose=True
        )
        self.memory.put(response.message)

        tool_calls = self.llm.get_tool_calls_from_response(
            response, error_on_no_tool_call=False
        )

        if not tool_calls:
            return StopEvent(
                result={"response": response.message.content, "sources": [*self.sources], "code": "no_tool_calls"}
            )
        else:
            return ToolCallEvent(tool_calls=tool_calls)

    @step
    async def handle_tool_calls(self, ev: ToolCallEvent) -> InputEvent:
        """Handle tool calls and get the output."""
        tool_calls = ev.tool_calls # get the tools that llm called
        tools_by_name = {list(tool_dict.values())[0].metadata.get_name(): list(tool_dict.values())[0] for tool_dict in
                         self.tools} # get all available tools
        tool_msgs = []
        # call tools -- safely!
        for tool_call in tool_calls:
            tool = tools_by_name.get(tool_call.tool_name)
            additional_kwargs = {
                "tool_call_id": tool_call.tool_id,
                "name": tool.metadata.get_name(),
            }
            if not tool:
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Tool {tool_call.tool_name} does not exist",
                        additional_kwargs=additional_kwargs,
                    )
                )
                continue

            try:
                logging.info(f"Calling tool: {tool.metadata.get_name()} with kwargs: {tool_call.tool_kwargs}")
                tool_output = tool(**tool_call.tool_kwargs)
                self.sources.append(tool_output)
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=tool_output.content,
                        additional_kwargs=additional_kwargs,
                    )
                )
            except Exception as e:
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Encountered error in tool call: {e}",
                        additional_kwargs=additional_kwargs,
                    )
                )

        for msg in tool_msgs:
            self.memory.put(msg)

        chat_history = self.memory.get()
        return InputEvent(input=chat_history)

    @staticmethod
    def get_tools_from_nodes(nodes: list) -> list[FunctionTool]:
        """Extract the tools from the most relevant nodes."""
        nodes.sort(key=lambda node: node.score, reverse=True) # reverse to make sure important nodes are prioritized
        files = {node.metadata.get("file_name") for node in nodes if node.metadata and "file_name" in node.metadata}
        files.add("static") # add the "static" tools
        return [item[file_name] for item in TOOL_REGISTRY for file_name in item if file_name in files]



