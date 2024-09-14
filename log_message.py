import supabase
from typing import Optional

def log_message(conversation_id: int, sender_id: str, message_content: str, sender_type: str) -> Optional[dict]:
    """Logs a message into the conversation."""
    new_message_data = {
        'conversation_id': conversation_id,
        'sender_id': sender_id,
        'message_content': message_content,
        'sender_type': sender_type  # Could be 'renter', 'owner', 'ai'
    }

    # Insert the message into the messages table
    message_response = supabase.table('messages').insert(new_message_data).execute()

    return message_response.data[0] if message_response.data else None
