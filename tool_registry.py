import asyncio
import inspect
import os
import threading
from asyncio import AbstractEventLoop
from typing import Callable, Type, Any, Optional
from pydantic import BaseModel
from llama_index.core.tools import ToolMetadata, FunctionTool

TOOL_REGISTRY = []
tools_loop: AbstractEventLoop = None
thread = None

def run_async_loop():
    global tools_loop
    tools_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(tools_loop)
    tools_loop.run_forever()


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
    """
    if not file_name:
        frame = inspect.stack()[1]
        file_name = os.path.basename(frame.filename)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func = function or func
        # Check if the function is a method (instance or class method)
        if inspect.signature(func).parameters:
            first_param = list(inspect.signature(func).parameters.keys())[0]
            if first_param == 'cls' or first_param == 'self':
                return func

        is_async = inspect.iscoroutinefunction(func)
        if is_async:
            global thread
            if not thread:
                thread = threading.Thread(target=run_async_loop)
                thread.start()

            nonlocal tool_metadata
            tool_metadata = tool_metadata or FunctionTool.from_defaults(func, name, description, return_direct, fn_schema).metadata
            def async_wrapper(*args, **kwargs):
                return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), tools_loop).result()
        TOOL_REGISTRY.append({
            file_name: FunctionTool.from_defaults(
                fn=func if not is_async else async_wrapper, #if not is_async else None,
                #async_fn=func if is_async else None,
                name=name,
                description=description,
                return_direct=return_direct,
                fn_schema=fn_schema,
                tool_metadata=tool_metadata
            )
        })

        return func

    return decorator
