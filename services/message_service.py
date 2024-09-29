from services.ai_service import AIService
from services.booking_service import BookingService
from services.conversation_service import ConversationService
from supabase_utils import supabase_client


class MessageService:

    @staticmethod
    def process_incoming_message(from_number, message_body):
        """
        Processes an incoming message from a guest or owner.
        Looks up the sender, determines the active booking, and adds the message to the conversation.
        If applicable, generates an AI response.
        """
        # Identify the sender (guest or owner) by phone number
        sender_info = MessageService._get_sender_info(from_number)

        if sender_info:
            sender_id = sender_info["id"]
            sender_type = sender_info["type"]

            # Step 1: Find the active booking for the sender by sender_id
            active_booking = BookingService.get_active_booking_by_sender_id(sender_id)
            if not active_booking:
                print(f"No active booking found for {sender_type} with ID {sender_id}")
                return

            booking_id = active_booking["id"]

            # Step 2: Get or create a conversation for the active booking
            conversation = ConversationService.get_or_create_conversation(booking_id)

            # Step 3: Add the incoming message to the conversation
            ConversationService.add_message(
                conversation_id=conversation["id"],
                sender_id=sender_id,
                sender_type=sender_type,
                message_body=message_body,
            )

            # Step 4: Get context (last 15 messages) for the AI to respond
            context_messages = ConversationService.get_last_n_messages(
                conversation_id=conversation["id"], limit=15
            )

            # Step 5: Generate AI response (if applicable)
            ai_response = AIService.generate_response(context_messages, booking_id)

            return ai_response  # Returning the AI response if there is one
        else:
            print(f"Sender not found for phone number {from_number}")
            return None

    @staticmethod
    def _get_sender_info(phone_number):
        """
        Helper method to retrieve the sender (guest or owner) information.
        """
        guest = (
            supabase_client.table("guests")
            .select("*")
            .eq("phone", phone_number)
            .single()
            .execute()
        )

        owner = (
            supabase_client.table("owners")
            .select("*")
            .eq("phone", phone_number)
            .single()
            .execute()
        )

        if guest.data:
            return {"id": guest.data["id"], "type": "guest"}
        elif owner.data:
            return {"id": owner.data["id"], "type": "owner"}
        return None
