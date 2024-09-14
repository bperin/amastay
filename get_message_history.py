# get_message_history.py
import supabase
from typing import List, Optional

def get_message_history(conversation_id: int, limit: int = 10) -> Optional[List[dict]]:
    """Fetches the recent message history for a conversation.
    
    Args:
        conversation_id (int): The ID of the conversation.
        limit (int): The maximum number of recent messages to retrieve.

    Returns:
        List[dict]: A list of recent messages ordered by their timestamp.
    """
    response = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at', desc=True).limit(limit).execute()

    return response.data if response.data else None

# Example usage
if __name__ == "__main__":
    conversation_id = 1
    message_history = get_message_history(conversation_id, limit=5)
    print(f"Recent message history: {message_history}")
