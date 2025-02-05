import inspect
import os
from typing import Callable, Type, Any, Optional
from pydantic import BaseModel
from llama_index.core.tools import ToolMetadata, FunctionTool

TOOL_REGISTRY = []


def register_tool(
        function: Callable[..., Any] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        return_direct: bool = False,
        fn_schema: Optional[Type[BaseModel]] = None,
        tool_metadata: Optional[ToolMetadata] = None,
        file_name: Optional[str] = None
):
    """
    A decorator to register a function as a tool with optional metadata.

    This decorator registers a function as a tool in a global tool registry, 
    allowing it to be used in various contexts, such as with Retrieval-Augmented Generation (RAG). 
    It automatically detects if the function is asynchronous and stores the appropriate function references 
    (synchronous or asynchronous) in the registry.

    Args:
        function (Callable[..., Any], optional): The function to register as a tool. Defaults to the function the decorator was used on.
        name (str, optional): The name of the tool. Defaults to the function name.
        description (str, optional): A description of the tool. Defaults to the function docstring.
        return_direct (bool, optional): Whether the tool should return the direct output of the function. Defaults to False.
        fn_schema (Type[BaseModel], optional): A Pydantic model to validate the function output. Defaults to None.
        tool_metadata (ToolMetadata, optional): Additional metadata for the tool. Defaults to None.
        file_name (str, optional): The name of the file where the tool is defined, this is used to split RAG documents, set to "static" if the tool should be used in every llm message.
    """
    if not file_name:
        frame = inspect.stack()[1]
        file_name = os.path.basename(frame.filename)

    def decorator(func: Callable[..., Any]):
        func = function or func
        is_async = inspect.iscoroutinefunction(func)

        TOOL_REGISTRY.append({file_name: FunctionTool.from_defaults(
            fn=func if not is_async else None,
            async_fn=func if is_async else None,
            name=name,
            description=description,
            return_direct=return_direct,
            fn_schema=fn_schema,
            tool_metadata=tool_metadata
        )})
        return func

    return decorator
