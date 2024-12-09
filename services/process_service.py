import logging
import os
import traceback
import requests

from phone_utils import PhoneUtils
from services.booking_service import BookingService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
from services.documents_service import DocumentsService
from services.property_information_service import PropertyInformationService
from services.property_service import PropertyService
from services.sagemaker_service import SageMakerService
from services.bedrock_service import BedrockService
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
        phone = PhoneUtils.normalize_phone(origination_number)
        guest = GuestService.get_guest_by_phone(phone)
        if not guest:
            logger.error(f"Guest lookup failed - Phone: {phone}")
            if send_message:
                PinpointService.send_sms(phone, os.getenv("SYSTEM_PHONE_NUMBER"), "We couldn't find your information. Please contact support.")
            return

        logger.info(f"Found guest: {guest.id} for phone: {phone}")

        # Booking lookup
        booking = BookingService.get_next_booking_by_guest_id(guest.id)
        if not booking:
            logger.error(f"No upcoming bookings found - Guest ID: {guest.id}")
            if send_message:
                PinpointService.send_sms(phone, os.getenv("SYSTEM_PHONE_NUMBER"), "We couldn't find any upcoming bookings for you. Please check your details.")
            return

        logger.info(f"Found booking: {booking.id} for guest: {guest.id}")

        # Property lookup
        property = PropertyService.get_property_by_booking_id(booking.property_id)
        if not property:
            logger.error(f"Property not found - Booking ID: {booking.id}")
            if send_message:
                PinpointService.send_sms(phone, os.getenv("SYSTEM_PHONE_NUMBER"), "We're sorry, but we couldn't find the property associated with your booking. Please contact support.")
            return

        logger.info(f"Found property: {property.id} for booking: {booking.id}")

        # Get property information and documents
        property_information = PropertyInformationService.get_property_information(property.id)
        property_documents = DocumentsService.get_documents_by_property_id(property.id)

        # Query AI model
        logger.info("Querying SageMaker model...")
        ai_response = BedrockService.query_model(booking=booking, property=property, guest=guest, prompt=message_body, message_id=message_id, property_information=property_information)

        logger.info(f"AI Response received: {ai_response[:100]}...")

        # Send response in chunks if needed
        if send_message:
            logger.info("Sending SMS response...")
            chunks = split_message_into_chunks(ai_response, 400)
            for chunk in chunks:
                PinpointService.send_sms(phone, os.getenv("SYSTEM_PHONE_NUMBER"), chunk)
                logger.info(f"SMS chunk sent: {chunk[:400]}...")

        return ai_response

    except Exception as e:
        handle_error(e, message_id, phone, message_body, send_message)


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


def handle_error(error: Exception, message_id: str, origination_number: str, message_body: str, send_message: bool = True) -> None:
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
    if send_message:
        try:
            PinpointService.send_sms(origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message)
            logger.info("Error message sent to user")
        except Exception as sms_error:
            logger.error(f"Failed to send error SMS: {str(sms_error)}")


def split_message_into_chunks(message: str, max_length: int = 400) -> list[str]:
    """
    Split a message into chunks that fit within SMS character limits.

    Args:
        message: The message to split
        max_length: Maximum length of each chunk (default 400 for SMS)

    Returns:
        List of message chunks
    """
    # If message is short enough, return as single chunk
    if len(message) <= max_length:
        return [message]

    chunks = []
    current_chunk = ""
    words = message.split()

    for word in words:
        # Check if adding the next word would exceed max_length
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += " " + word if current_chunk else word
        else:
            # Save current chunk and start new one
            chunks.append(current_chunk)
            current_chunk = word

    # Add the last chunk if there is one
    if current_chunk:
        chunks.append(current_chunk)

    # Add chunk numbers if there are multiple chunks
    if len(chunks) > 1:
        chunks = [f"({i+1}/{len(chunks)}) {chunk}" for i, chunk in enumerate(chunks)]

    return chunks
