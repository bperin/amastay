from supabase_utils import supabase
from datetime import datetime


def store_message(conversation_id: int, content: str, direction: str) -> dict:
    """
    Stores a message in the messages table.

    Args:
        conversation_id (int): The ID of the conversation.
        content (str): The message content.
        direction (str): Indicates if the message is from 'user' or 'ai'.

    Returns:
        dict: The inserted message record.
    """
    new_message_data = {
        "conversation_id": conversation_id,
        "message_content": content,
        "direction": direction,  # 'user' or 'ai'
        "timestamp": datetime.now(),
    }

    response = supabase.table("messages").insert(new_message_data).execute()

    return response.data[0] if response.data else None


# Example usage
if __name__ == "__main__":
    conversation_id = 1
    message_content = "What time is check-out?"
    direction = "user"
    stored_message = store_message(conversation_id, message_content, direction)
    print(f"Message stored: {stored_message}")
