# create_conversation.py
from utils import supabase
from typing import Optional

def create_or_get_conversation(booking_id: int, property_id: int) -> Optional[dict]:
    """Creates or fetches a conversation for a booking and property."""
    # Check if a conversation exists for this booking and property
    response = supabase.table('conversations').select('*').eq('booking_id', booking_id).eq('property_id', property_id).execute()

    if response.data:
        return response.data[0]  # Return the existing conversation

    # If no conversation exists, create a new one
    new_conversation_data = {
        'booking_id': booking_id,
        'property_id': property_id,
        'status': 'active'
    }

    conversation_response = supabase.table('conversations').insert(new_conversation_data).execute()

    return conversation_response.data[0] if conversation_response.data else None

# Example usage
if __name__ == "__main__":
    booking_id = 1
    property_id = 1
    conversation = create_or_get_conversation(booking_id, property_id)
    print(f"Conversation created or fetched: {conversation}")
