from typing import Any
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step
from llama_index.llms.openai import OpenAI


from tool_registry import TOOL_REGISTRY
from .response_event import InputEvent, ToolCallEvent




class FunctionCallingAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: FunctionCallingLLM | None = None,
        system_prompt: str = "",
        n_message_history: int = 3,
        index_handler = None,
        tools,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tools = tools
        self.llm = llm or OpenAI()
        assert self.llm.metadata.is_function_calling_model
        self.sys_message = ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
        self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[self.sys_message])
        self.sources = []
        self.n_message_history = n_message_history
        self.index_handler = index_handler
        self.current_tools = []

    @step
    async def prepare_chat_history(self, ev: StartEvent) -> InputEvent:
        """Prepare chat history for the LLM."""
        # clear sources
        self.sources = []
        last_x_messages = self.memory.get_last_messages(n=self.n_message_history)
        self.memory = ChatMemoryBuffer.from_defaults(llm=self.llm, chat_history=last_x_messages)
        # get user input
        user_input = ev.input
        user_msg = ChatMessage(role="user", content=user_input)
        self.memory.put(user_msg)

        # get chat history
        chat_history = self.memory.get()

        return InputEvent(input=chat_history, message=user_input)
    @step
    async def handle_llm_input(
        self, ev: InputEvent
    ) -> ToolCallEvent | StopEvent:
        """Handle input to the LLM and retreive the most relevant tools using RAG."""
        message = ev.message
        if message !="p":
            # retrieve relevant nodes
            nodes = self.index_handler.retrieve_nodes(message)
            self.current_tools = FunctionCallingAgent.get_tools_from_nodes(nodes=nodes) or []
        chat_history = ev.input
        response = await self.llm.achat_with_tools(
            tools=self.current_tools, chat_history=chat_history
        )
        self.memory.put(response.message)

        tool_calls = self.llm.get_tool_calls_from_response(
            response, error_on_no_tool_call=False
        )

        if not tool_calls:
            return StopEvent(
                result={"response": response.message.content, "sources": [*self.sources]}
            )
        else:
            return ToolCallEvent(tool_calls=tool_calls)

    @step
    async def handle_tool_calls(self, ev: ToolCallEvent) -> InputEvent:
        """Handle tool calls and get the output."""
        tool_calls = ev.tool_calls
        tools_by_name = {list(tool_dict.values())[0].metadata.get_name(): list(tool_dict.values())[0] for tool_dict in
                         self.tools}
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
        return InputEvent(input=chat_history, message="p")

    @staticmethod
    def get_tools_from_nodes(nodes: list):
        """Extract the tools from the most relevant nodes."""
        nodes.sort(key=lambda node: node.score, reverse=True) # reverse to make sure important nodes are prioritized
        files = {node.metadata.get("file_name") for node in nodes if node.metadata and "file_name" in node.metadata}
        return [item[file_name] for item in TOOL_REGISTRY for file_name in item if file_name in files]


