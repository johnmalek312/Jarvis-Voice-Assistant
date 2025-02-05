"""This module contains functions for working with Python code and math. like executing code in a thread."""

import threading
from typing import Annotated


from tool_registry import register_tool


@register_tool()
def execute_code(code: Annotated[str, "The python code to execute."], timeout: Annotated[float, "The maximum time to allow for code execution in seconds"] = 7) -> str:
    """Execute Python code in a thread and return the output. Can be used for math or other code execution."""
    # not very safe, the thread could run indefinitely and consume a lot of resources.
    def target(output):
        try:
            exec(code, {}, output)
        except Exception as e:
            output['error'] = str(e)

    output = {}
    thread = threading.Thread(target=target, args=(output,))
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return "Error: Code execution timed out"

    if 'error' in output:
        return f"Error: {output['error']}"

    return str(output)
