"""This module adds functions that allow the llm to manage the workflow of the llm.
For example, this module provides functions that retrieve the amount of tokens spent, reset the token counter, and reset the chat messages."""
from typing import Annotated

from tool_registry import register_tool
from .data_manager import DataManager
from config import Top_K_Retriever
@register_tool()
def get_tokens_spent():
    """Returns the amount of tokens spent in the current session or since the last token reset.
    """
    return (
        f"Token Usage Report in this session or since the last token reset:\n"
        f"• {DataManager.token_counter.total_embedding_token_count:,} tokens used for embeddings\n"
        f"• {DataManager.token_counter.prompt_llm_token_count:,} tokens used in prompts\n"
        f"• {DataManager.token_counter.completion_llm_token_count:,} tokens used in completions\n"
        f"• {DataManager.token_counter.total_llm_token_count:,} total tokens used prompts and completion"
    )

@register_tool()
def reset_token_counter():
    """Resets the token counter.
    """
    DataManager.token_counter.reset_counts()
    return "Token counter has been reset."

@register_tool()
def reset_chat_messages():
    """Resets the chat messages of the current llm or voice assistant conversation.
    """
    DataManager.llm.reset_messages()
    return "Chat messages have been reset."

@register_tool()
def set_max_message_history(max_message_history: Annotated[int, "The maximum number of user chat messages to store."]):
    """Sets the maximum number of user chat messages to store in the llm or voice assistant conversation.
    """
    if max_message_history < 1:
        return "Max user message history must be at least 1."
    DataManager.llm.agent_flow.n_message_history = max_message_history
    return f"Max user message history has been set to {max_message_history}."

@register_tool()
def get_max_message_history():
    """Returns the maximum number of user chat messages to store in the llm or voice assistant conversation.
    """
    return f"Max user message history is {DataManager.llm.agent_flow.n_message_history}."


@register_tool(file_name="static")
def query_tool(query: Annotated[str,
"Focus on the required tool or action, not the task. Use general terms to describe the functionality rather than "
"task-specific details.\n\n"
"Example:\n\n"
"    Task: 'Send an email to my friend.'\n"
"    Bad query: 'Email my friend'\n"
"    Good query: 'Function to send an email'\n"
"    General Guideline: Use terms like 'function to send,' 'function to open,' or 'function to process' to emphasize the tool rather than the specific task."
]) -> str:  # used to retrieve relevant tools
    """Fetches new function tools using retrieval-augmented generation (RAG) based on the query and updates the current tools with the relevant ones.

        This can only be used once per message, as it will overwrite previous tools.

        YOU MUST NOT USE THIS FUNCTION MORE THAN ONCE PER MESSAGE!
    """
    if Top_K_Retriever == -1:
        return "All tools are already in the query."
    DataManager.llm.agent_flow.get_tools_from_nodes(DataManager.llm.index_handler.retrieve_nodes(query))
    return "Fetched new tools based on the query."
