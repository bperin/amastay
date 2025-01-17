import logging
import os
import traceback
from typing import List, Optional
import requests

from models.document_model import Document
from phone_utils import PhoneUtils
from services import message_service
from services.booking_service import BookingService
from services.llama_service_vertex import LlamaService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
from services.documents_service import DocumentsService
from services.property_information_service import PropertyInformationService
from services.property_service import PropertyService
from services.guest_service import GuestService

logger = logging.getLogger(__name__)


def is_message_from_ai(origination_number: str) -> bool:
    """Check if message is from AI system"""
    ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
    cleaned_orig = origination_number.lstrip("+")
    cleaned_ai = ai_number.lstrip("+")
    return cleaned_orig == cleaned_ai


def send_sms_message(phone: str, message: str, send_message: bool = True) -> None:
    """
    Helper method to send SMS messages v ia Pinpoint.

    Args:
        phone: Recipient's phone number
        message: Message content
        send_message: Flag to control if message should be sent
    """
    if send_message:
        try:
            system_phone = os.getenv("SYSTEM_PHONE_NUMBER")
            PinpointService.send_sms(phone, system_phone, message)
            logger.info(f"SMS sent to {phone}: {message[:50]}...")
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")


def handle_incoming_sms(message_id: str, origination_number: str, message_body: str, send_message: bool = True, current_user_id: Optional[str] = None) -> str:
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
            send_sms_message(phone, "We couldn't find your information. Please contact support.", send_message)
            return

        logger.info(f"Found guest: {guest.id} for phone: {phone}")

        # Booking lookup
        booking = BookingService.get_next_booking_by_guest_id(guest.id)
        if not booking:
            logger.error(f"No upcoming bookings found - Guest ID: {guest.id}")
            send_sms_message(phone, "We couldn't find any upcoming bookings for you. Please check your details.", send_message)
            return

        logger.info(f"Found booking: {booking.id} for guest: {guest.id}")

        # Property lookup
        property = PropertyService.get_property_by_booking_id(booking.property_id)
        if not property:
            logger.error(f"Property not found - Booking ID: {booking.id}")
            send_sms_message(phone, "We're sorry, but we couldn't find the property associated with your booking. Please contact support.", send_message)
            return

        logger.info(f"Found property: {property.id} for booking: {booking.id}")

        # Get property information and documents
        property_information = PropertyInformationService.get_property_information_by_property_id(property.id)
        property_documents = DocumentsService.get_documents_by_property_id(property.id)
        document_text = process_property_documents(property_documents, property.id)

        # add user message to DB
        message = MessageService.add_message(booking_id=booking.id, sender_id=guest.id, sender_type=0, content=message_body)  # user type

        # Query AI model
        logger.info("Prompting Llama model...")

        result = LlamaService.prompt(booking_id=booking.id, prompt=message_body)

        logger.info(f"AI Response received: {result[:100]}...")

        MessageService.add_message(booking_id=booking.id, sender_id=None, sender_type=1, content=result, question_id=message.id)

        # Send response in chunks if needed
        if send_message:
            logger.info("Sending SMS response...")
            chunks = split_message_into_chunks(result)
            for chunk in chunks:
                send_sms_message(phone, chunk, send_message)

        return result

    except Exception as e:
        handle_error(e, message_id, phone, message_body, send_message)


def process_property_documents(documents: List[Document], property_id: str) -> str:
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

    return "\n".join(processed_texts)


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
    send_sms_message(origination_number, error_message, send_message)


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
