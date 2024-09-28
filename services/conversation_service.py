from datetime import datetime
from supabase_utils import supabase_client


class ConversationService:

    @staticmethod
    def get_or_create_conversation(booking_id):
        # Query the conversations table to check if a conversation exists for the given booking_id
        response = (
            supabase_client.table("conversations")
            .select("*")
            .eq("booking_id", booking_id)
            .single()
            .execute()
        )

        if response.data:
            return response.data
        else:
            # If no conversation exists, create a new one
            new_conversation = {"booking_id": booking_id}
            response = (
                supabase_client.table("conversations")
                .insert(new_conversation)
                .execute()
            )
            return response.data[0] if response.data else None

    @staticmethod
    def add_message(conversation_id, sender_id, sender_type, message):
        # Insert a new message into the messages table with the conversation_id
        new_message = {
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "sender_type": sender_type,
            "message": message,
            "created_at": datetime.now(),  # Assuming there's a timestamp field
        }
        supabase_client.table("messages").insert(new_message).execute()
