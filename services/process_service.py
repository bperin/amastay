import logging
import os
import traceback
import requests
from services.booking_service import BookingService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
from services.documents_service import DocumentsService
from services.property_information_service import PropertyInformationService
from services.property_service import PropertyService
from services.sagemaker_service import SageMakerService
from supabase_utils import supabase_client


class ProcessService:
    logger = logging.getLogger(__name__)

    _sagemaker_service = None

    @classmethod
    def get_sagemaker_service(cls):
        return SageMakerService()

    @classmethod
    def handle_incoming_sms(cls, message_id, origination_number, message_body):
        """
        Handles incoming SMS between a guest and the AI.
        """
        try:
            cls.logger.info(f"Processing SMS - ID: {message_id}, From: {origination_number}, Message: {message_body}")

            if cls.is_message_from_ai(origination_number):
                cls.logger.info(f"Message from AI, ignoring: {message_body}")
                return

            from services.guest_service import GuestService

            # Check for existing message
            existing_message = MessageService.get_message_by_sms_id(message_id)
            if existing_message:
                cls.logger.info(f"Message with SMS ID {message_id} already processed, skipping")
                return

            # Guest lookup
            guest = GuestService.get_guest_by_phone(origination_number)
            if not guest:
                cls.logger.error(f"Guest lookup failed - Phone: {origination_number}")
                error_message = "We couldn't find your information. Please contact support."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                return

            cls.logger.info(f"Found guest: {guest.id} for phone: {origination_number}")

            # Booking lookup
            booking = BookingService.get_next_booking_by_guest_id(guest.id)
            if not booking:
                cls.logger.error(f"No upcoming bookings found - Guest ID: {guest.id}, Phone: {origination_number}")
                error_message = "We couldn't find any upcoming bookings for you. Please check your details."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                return

            cls.logger.info(f"Found booking: {booking.id} for guest: {guest.id}")

            # Property lookup
            property = PropertyService.get_property_by_booking_id(booking.property_id)
            if not property:
                cls.logger.error(f"Property not found - Booking ID: {booking.id}, Property ID: {booking.property_id}")
                error_message = "We're sorry, but we couldn't find the property associated with your booking. Please contact support."
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                return

            cls.logger.info(f"Found property: {property.id} for booking: {booking.id}")

            property_information = PropertyInformationService.get_property_information(property.id)
            if not property_information:
                cls.logger.info(f"No property information found for property ID {property.id}")
            else:
                cls.logger.info(f"Retrieved property information for property ID {property.id}")

            property_documents = DocumentsService.get_documents_by_property_id(property.id)

            if not property_documents:
                cls.logger.info(f"No documents found for property ID {property.id}")
            else:
                cls.logger.info(f"Retrieved {len(property_documents)} documents for property ID {property.id}")

            processed_documents = []
            all_document_text = ""
            if property_documents:
                cls.logger.info(f"Found {len(property_documents)} documents for property ID {property.id}")
                for document in property_documents:
                    cls.logger.info(f"Attempting to read document: {document.file_url}")
                    try:
                        response = requests.get(document.file_url)
                        response.raise_for_status()  # Raise an error for bad responses
                        plain_text = response.text
                        processed_documents.append({"name": document.file_url, "content": plain_text})
                        all_document_text += plain_text + "\n\n"
                        cls.logger.info(f"Successfully read document: {document.file_url}")
                    except requests.exceptions.RequestException as e:
                        cls.logger.warning(f"Could not read content for document: {document.file_url}, error: {e}")

                cls.logger.info(f"Processed {len(processed_documents)} documents for property ID {property.id}")
            else:
                cls.logger.info("No property documents to process")

            # SageMaker query
            cls.logger.info("Initializing SageMaker service...")
            sagemaker_service = cls.get_sagemaker_service()

            cls.logger.info("Querying SageMaker model...")
            ai_response = sagemaker_service.query_model(booking=booking, property=property, guest=guest, prompt=message_body, message_id=message_id, property_information=property_information, all_document_text=all_document_text)

            cls.logger.info(f"AI Response received: {ai_response[:100]}...")  # Log first 100 chars

            # Send response
            cls.logger.info("Sending SMS response...")
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), ai_response)
            cls.logger.info("SMS response sent successfully")

        except Exception as e:
            cls.logger.error("========== ERROR PROCESSING SMS ==========")
            cls.logger.error(f"Message ID: {message_id}")
            cls.logger.error(f"From: {origination_number}")
            cls.logger.error(f"Message: {message_body}")
            cls.logger.error(f"Error: {str(e)}")
            cls.logger.error("Traceback:")
            cls.logger.error(traceback.format_exc())
            cls.logger.error("=======================================")

            error_message = "We're sorry, but there was an error processing your message. Please try again later."
            try:
                PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
                cls.logger.info("Error message sent to user")
            except Exception as sms_error:
                cls.logger.error(f"Failed to send error SMS: {str(sms_error)}")

    @staticmethod
    def is_message_from_ai(origination_number: str) -> bool:
        ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
        # Strip any leading + from both numbers for comparison
        cleaned_orig = origination_number.lstrip("+")
        cleaned_ai = ai_number.lstrip("+")
        return cleaned_orig == cleaned_ai
