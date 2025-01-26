from llama_index.core.llms import ChatMessage, MessageRole
from typing import List
from llama_index.core.memory import ChatMemoryBuffer

def get_last_messages(
    self: ChatMemoryBuffer, n: int = 10
) -> List[ChatMessage] | bool:
    """
    Retrieves system messages and messages before the last N user messages from the end.
    Includes ^all^ system messages.
    """



    chat_history = self.get()
    if n >= len(chat_history):
        return chat_history
    if n >= len([chat_message for chat_message in chat_history if chat_message.role == MessageRole.USER]):
        return chat_history
    user_message_count = 0
    cutoff_index = -1

    if n == 0:  # If n is 0, only return system messages
        return [msg for msg in chat_history if msg.role == MessageRole.SYSTEM]


    for i in range(len(chat_history) - 1, -1, -1):  # Iterate backwards
        message = chat_history[i]
        if message.role == MessageRole.USER:
            user_message_count += 1
        if user_message_count >= n:
            cutoff_index = i
            break


    if cutoff_index == -1:  # Not enough user messages, return all history
        return chat_history

    # Collect the last n user messages and all messages after the cutoff
    messages_after_cutoff = chat_history[cutoff_index:]

    # Extract system messages from all history
    system_messages = [
        msg for msg in chat_history if msg.role == MessageRole.SYSTEM
    ]

    # Check if there are any system messages before the first user message
    system_messages_before_cutoff = [
        msg for msg in system_messages if chat_history.index(msg) < cutoff_index
    ]

    # Return system messages before the cutoff, and messages from cutoff onward
    return system_messages_before_cutoff + messages_after_cutoff



# Monkey patch
ChatMemoryBuffer.get_last_messages = get_last_messages
