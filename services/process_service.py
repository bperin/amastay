import logging
import os
import tempfile
import time
from services.booking_service import BookingService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
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
        try:
            # Step 1: Check if the SMS is from the AI (ignore AI messages)
            if ProcessService.is_message_from_ai(origination_number):
                logging.info(f"Message from AI, ignoring: {message_body}")
                return

            # Step 1: Get the guest from the guest service by phone number
            from services.guest_service import GuestService

            guest = GuestService.get_guest_by_phone(origination_number)
            if not guest:
                logging.warning(f"No guest found for phone number {origination_number}")
                error_message = (
                    "We couldn't find your information. Please contact support."
                )
                PinpointService.send_sms(
                    origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
                )
                return

            # Step 2: Proceed with booking retrieval
            booking = BookingService.get_next_booking_by_guest_id(guest.id)
            if not booking:
                # No upcoming bookings, respond with an error message
                error_message = "We couldn't find any upcoming bookings for you. Please check your details."
                PinpointService.send_sms(
                    origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
                )
                logging.warning(
                    f"No upcoming bookings for phone number {origination_number}"
                )
                return

            # Step 3: Generate AI response
            ai_response = ProcessService.model_service.query_model(
                booking.id, message_body
            )
            breakpoint()
            # Step 7: Send the AI response back to the guest
            PinpointService.send_sms(
                origination_number,
                os.getenv("SYSTEM_PHONE_NUMBER"),
                ai_response["response"],
            )
            breakpoint()
        except Exception as e:
            logging.error(f"Error processing incoming SMS: {str(e)}")
            # Optionally, send an error message to the user
            error_message = "We're sorry, but there was an error processing your message. Please try again later."
            PinpointService.send_sms(
                origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
            )

    @staticmethod
    def is_message_from_ai(origination_number: str) -> bool:
        ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
        return origination_number == ai_number
