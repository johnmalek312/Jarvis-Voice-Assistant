from llama_index.core.llms import ChatMessage
from llama_index.core.tools import ToolSelection, ToolOutput, FunctionTool
from llama_index.core.workflow import Event


class InputEvent(Event):
    input: list[ChatMessage]
    message: str = ""


class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]


class FunctionOutputEvent(Event):
    output: ToolOutput


class ToolResultEvent(Event):
    input: list[ChatMessage]
    query: str | None = None # query used to retrieve different tools
