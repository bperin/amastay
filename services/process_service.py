import logging
import os
import requests
from services.booking_service import BookingService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
from services.documents_service import DocumentsService
from services.property_information_service import PropertyInformationService
from services.property_service import PropertyService
from services.model_service import ModelService
from supabase_utils import supabase_client


class ProcessService:
    model_service = None

    @classmethod
    def initialize(cls):
        """Initialize the singleton ModelService instance"""
        if cls.model_service is None:
            cls.model_service = ModelService()

    @classmethod
    def handle_incoming_sms(cls, message_id, origination_number, message_body):
        """
        Handles incoming SMS between a guest and the AI.
        Retrieves guest information for sender_id, saves the guest message before querying history,
        and saves the AI response after generating it.
        """
        try:
            if cls.model_service is None:
                cls.initialize()

            if cls.is_message_from_ai(origination_number):
                logging.info(f"Message from AI, ignoring: {message_body}")
                return

            from services.guest_service import GuestService

            # Check if we've already processed this SMS message
            existing_message = MessageService.get_message_by_sms_id(message_id)
            if existing_message:
                logging.info(f"Message with SMS ID {message_id} already processed, skipping")
                return

            guest = GuestService.get_guest_by_phone(origination_number)
            if not guest:
                logging.warning(f"No guest found for phone number {origination_number}")
                error_message = "We couldn't find your information. Please contact support."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                return

            booking = BookingService.get_next_booking_by_guest_id(guest.id)
            if not booking:
                error_message = "We couldn't find any upcoming bookings for you. Please check your details."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                logging.warning(f"No upcoming bookings for phone number {origination_number}")
                return

            property = PropertyService.get_property_by_booking_id(booking.property_id)

            if not property:
                logging.warning(f"No property found for booking ID {booking.id}")
                error_message = "We're sorry, but we couldn't find the property associated with your booking. Please contact support."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                return

            property_information = PropertyInformationService.get_property_information(property.id)
            if not property_information:
                logging.info(f"No property information found for property ID {property.id}")
            else:
                logging.info(f"Retrieved property information for property ID {property.id}")

            property_documents = DocumentsService.get_documents_by_property_id(property.id)

            if not property_documents:
                logging.info(f"No documents found for property ID {property.id}")
            else:
                logging.info(f"Retrieved {len(property_documents)} documents for property ID {property.id}")

            processed_documents = []
            all_document_text = ""
            if property_documents:
                logging.info(f"Found {len(property_documents)} documents for property ID {property.id}")
                for document in property_documents:
                    logging.info(f"Attempting to read document: {document.file_url}")
                    try:
                        response = requests.get(document.file_url)
                        response.raise_for_status()  # Raise an error for bad responses
                        plain_text = response.text
                        processed_documents.append({"name": document.file_url, "content": plain_text})
                        all_document_text += plain_text + "\n\n"
                        logging.info(f"Successfully read document: {document.file_url}")
                    except requests.exceptions.RequestException as e:
                        logging.warning(f"Could not read content for document: {document.file_url}, error: {e}")

                logging.info(f"Processed {len(processed_documents)} documents for property ID {property.id}")
            else:
                logging.info("No property documents to process")

            ai_response = ProcessService.model_service.query_model(
                booking,
                property,
                guest,
                message_body,
                message_id,
                property_information,
                all_document_text,
            )

            logging.info(f"AI: Response: {ai_response}")

            PinpointService.send_sms(
                origination_number,
                os.getenv("SYSTEM_PHONE_NUMBER"),
                ai_response["response"],
            )

        except Exception as e:
            logging.error(f"Error processing incoming SMS: {str(e)}")
            error_message = "We're sorry, but there was an error processing your message. Please try again later."
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)

    @staticmethod
    def is_message_from_ai(origination_number: str) -> bool:
        ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
        # Strip any leading + from both numbers for comparison
        cleaned_orig = origination_number.lstrip("+")
        cleaned_ai = ai_number.lstrip("+")
        return cleaned_orig == cleaned_ai
