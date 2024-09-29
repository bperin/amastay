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

    @staticmethod
    def get_conversation_participants(booking_id):
        """
        Retrieves all participants (guests and potentially the property owner)
        for a given conversation linked to a booking.

        Args:
            booking_id (str): The booking ID for the conversation.

        Returns:
            list: A list of phone numbers of the participants.
        """
        try:
            # Query to get guests associated with the booking
            participants_response = (
                supabase_client.from_("booking_guests")
                .select(
                    """
                guest_id, guests(phone_number)
                """
                )
                .eq("booking_id", booking_id)
                .execute()
            )

            if participants_response.error:
                print(f"Error fetching participants: {participants_response.error}")
                return None

            # Extract the guest phone numbers from the response
            guests_phone_numbers = [
                participant["guests"]["phone_number"]
                for participant in participants_response.data
            ]

            # Optionally, query for the owner’s phone number (if needed)
            owner_response = (
                supabase_client.from_("bookings")
                .select(
                    """
                owner_id, owners(phone_number)
                """
                )
                .eq("id", booking_id)
                .single()
                .execute()
            )

            if owner_response.error:
                print(f"Error fetching owner: {owner_response.error}")
                return None

            owner_phone_number = owner_response.data["owners"]["phone_number"]

            # Combine guest phone numbers and owner phone number
            all_participants = guests_phone_numbers + [owner_phone_number]

            return all_participants

        except Exception as e:
            print(f"An error occurred while fetching participants: {e}")
            return None

    @staticmethod
    def get_last_n_messages(conversation_id, limit=15):
        """
        Retrieves the last 'n' messages for a given conversation, ordered by the sent time.

        Args:
            conversation_id (str): The ID of the conversation to fetch messages from.
            limit (int): The number of messages to retrieve. Defaults to 15.

        Returns:
            list: A list of messages, with the most recent messages first.
        """
        try:
            # Query to get the last 'n' messages from the 'messages' table, ordered by 'sent_at' descending
            response = (
                supabase_client.from_("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("sent_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Check if the response has data
            if response.data:
                return response.data
            else:
                print(f"No messages found for conversation ID {conversation_id}")
                return []

        except Exception as e:
            print(f"An error occurred while fetching messages: {e}")
            return []
