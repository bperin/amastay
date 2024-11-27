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
from services.guest_service import GuestService

logger = logging.getLogger(__name__)


def is_message_from_ai(origination_number: str) -> bool:
    """Check if message is from AI system"""
    ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
    cleaned_orig = origination_number.lstrip("+")
    cleaned_ai = ai_number.lstrip("+")
    return cleaned_orig == cleaned_ai


def handle_incoming_sms(message_id: str, origination_number: str, message_body: str, send_message: bool = True) -> str:
    """Handle incoming SMS between a guest and the AI"""
    try:
        logger.info(f"Processing SMS - ID: {message_id}, From: {origination_number}, Message: {message_body}")

        if is_message_from_ai(origination_number):
            logger.info(f"Message from AI, ignoring: {message_body}")
            return

        # Check for existing message
        existing_message = MessageService.get_message_by_sms_id(message_id)
        if existing_message:
            logger.info(f"Message with SMS ID {message_id} already processed, skipping")
            return

        # Guest lookup
        guest = GuestService.get_guest_by_phone(origination_number)
        if not guest:
            logger.error(f"Guest lookup failed - Phone: {origination_number}")
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), "We couldn't find your information. Please contact support.")
            return

        logger.info(f"Found guest: {guest.id} for phone: {origination_number}")

        # Booking lookup
        booking = BookingService.get_next_booking_by_guest_id(guest.id)
        if not booking:
            logger.error(f"No upcoming bookings found - Guest ID: {guest.id}")
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), "We couldn't find any upcoming bookings for you. Please check your details.")
            return

        logger.info(f"Found booking: {booking.id} for guest: {guest.id}")

        # Property lookup
        property = PropertyService.get_property_by_booking_id(booking.property_id)
        if not property:
            logger.error(f"Property not found - Booking ID: {booking.id}")
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), "We're sorry, but we couldn't find the property associated with your booking. Please contact support.")
            return

        logger.info(f"Found property: {property.id} for booking: {booking.id}")

        # Get property information and documents
        property_information = PropertyInformationService.get_property_information(property.id)
        property_documents = DocumentsService.get_documents_by_property_id(property.id)

        # Process documents
        all_document_text = process_property_documents(property_documents, property.id)

        # Query AI model
        logger.info("Querying SageMaker model...")
        ai_response = SageMakerService.query_model(booking=booking, property=property, guest=guest, prompt=message_body, message_id=message_id, property_information=property_information, all_document_text=all_document_text)

        logger.info(f"AI Response received: {ai_response[:100]}...")

        # Send response
        if send_message:
            logger.info("Sending SMS response...")
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), ai_response)
            logger.info("SMS response sent successfully")

        return ai_response

    except Exception as e:
        handle_error(e, message_id, origination_number, message_body)


def process_property_documents(documents, property_id: str) -> str:
    """Process property documents and return combined text"""
    if not documents:
        logger.info(f"No documents found for property ID {property_id}")
        return ""

    logger.info(f"Processing {len(documents)} documents for property ID {property_id}")
    processed_texts = []

    for document in documents:
        try:
            response = requests.get(document.file_url)
            response.raise_for_status()
            processed_texts.append(response.text)
            logger.info(f"Successfully processed document: {document.file_url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not read content for document: {document.file_url}, error: {e}")

    return "\n\n".join(processed_texts)


def handle_error(error: Exception, message_id: str, origination_number: str, message_body: str) -> None:
    """Handle and log errors during SMS processing"""
    logger.error("========== ERROR PROCESSING SMS ==========")
    logger.error(f"Message ID: {message_id}")
    logger.error(f"From: {origination_number}")
    logger.error(f"Message: {message_body}")
    logger.error(f"Error: {str(error)}")
    logger.error("Traceback:")
    logger.error(traceback.format_exc())
    logger.error("=======================================")

    error_message = "We're sorry, but there was an error processing your message. Please try again later."
    try:
        PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
        logger.info("Error message sent to user")
    except Exception as sms_error:
        logger.error(f"Failed to send error SMS: {str(sms_error)}")
