import inspect
import os
from typing import Callable, Type, Any, Optional
from pydantic import BaseModel
from llama_index.core.tools import ToolMetadata, FunctionTool

TOOL_REGISTRY = []

def register_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    return_direct: bool = False,
    fn_schema: Optional[Type[BaseModel]] = None,
    tool_metadata: Optional[ToolMetadata] = None
):
    """
    A decorator to register a function as a tool with optional metadata.

    This decorator registers a function as a tool in a global tool registry, 
    allowing it to be used in various contexts, such as with Retrieval-Augmented Generation (RAG). 
    It automatically detects if the function is asynchronous and stores the appropriate function references 
    (synchronous or asynchronous) in the registry.
    """
    frame = inspect.stack()[1]
    file_name = os.path.basename(frame.filename)
    def decorator(func: Callable[..., Any]):
        is_async = inspect.iscoroutinefunction(func)
        TOOL_REGISTRY.append({file_name:FunctionTool.from_defaults(**{
            'fn': func if not is_async else None,
            'async_fn': func if is_async else None,
            'name': name,
            'description': description,
            'return_direct': return_direct,
            'fn_schema': fn_schema,
            'tool_metadata': tool_metadata
        })})
        return func

    return decorator