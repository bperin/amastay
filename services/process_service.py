import os
from services.booking_service import BookingService
from services.message_service import MessageService
from services.sms_service import SmsService
from services.model_service import ModelService
from supabase_utils import supabase_client

class ProcessService:
    model_service = ModelService()

    @staticmethod
    def handle_incoming_sms(sms_id, origination_number, message_body):
        """
        Handles incoming SMS between a guest and the AI.
        Retrieves guest information for sender_id, saves the guest message before querying history,
        and saves the AI response after generating it.
        """
        # Step 1: Check if the SMS is from the AI (ignore AI messages)
        if ProcessService.is_message_from_ai(origination_number):
            print(f"Message from AI, ignoring: {message_body}")
            return

        # Step 2: Retrieve the next upcoming booking using the phone number
        booking = BookingService.get_next_upcoming_booking_by_phone(origination_number)
        if not booking:
            # No upcoming bookings, respond with an error message
            error_message = "We couldn't find any upcoming bookings for you. Please check your details."
            SmsService.send_sms(
                origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
            )
            print(f"No upcoming bookings for phone number {origination_number}")
            return

        # Step 3: Retrieve the guest information based on the phone number
        guest = BookingService.get_guest_by_phone(origination_number)
        if not guest:
            print(f"Guest not found for phone number {origination_number}")
            return

        # Step 4: Save the incoming guest message to the database first
        new_message = MessageService.add_message(
            booking_id=booking.id,
            sender_id=guest.id,
            sender_type=0,  # 0 for guest
            content=message_body,
            sms_id=sms_id,
        )

        # Step 5: Retrieve message history for the booking (including the just-added message)
        message_history = MessageService.get_messages_by_booking(booking.id)

        # Step 6: Prepare messages for the model
        messages = [{"role": "user" if msg.sender_type == 0 else "assistant", "content": msg.content} for msg in reversed(message_history)]

        # Step 7: Generate a response from the AI service
        ai_response = ProcessService.model_service.query_model(messages)

        # Step 8: Save the AI's response in the database
        ai_message = MessageService.add_message(
            booking_id=booking.id,
            sender_id=None,  # AI doesn't have a guest ID
            sender_type=1,  # 1 for AI
            content=ai_response,
            sms_id=None,  # AI-generated messages won't have an SMS ID
        )

        # Step 9: Send the AI response back to the guest
        SmsService.send_sms(
            origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), ai_response
        )

        # Step 10: Once the SMS is successfully sent, update the original guest message with the sms_id
        if new_message:
            MessageService.update_message_sms_id(new_message.id, sms_id)

    @staticmethod
    def is_message_from_ai(origination_number: str) -> bool:
        ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
        return origination_number == ai_number
