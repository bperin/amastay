import json
import boto3
import os
import logging
import sys

service_dir = os.path.join(os.path.dirname(__file__), "services")
sys.path.append(service_dir)

from services.booking_service import BookingService
from services.conversation_service import ConversationService
from services.message_service import MessageService

# Set up AWS Pinpoint client
pinpoint = boto3.client("pinpoint")

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define system number or other identifiers (AI/System originator)
SYSTEM_NUMBER = os.getenv(
    "SYSTEM_PHONE_NUMBER"
)  # Add your system's phone number to environment variables


def lambda_handler(event, context):
    """
    Lambda function to handle incoming SMS messages, look up conversation, and send the message to all participants (guests and AI).
    """
    for record in event["Records"]:
        message_body = record["Sns"]["Message"]["MessageBody"]
        origination_number = record["Sns"]["Message"]["OriginationNumber"]

        logger.info(f"Received message from {origination_number}: {message_body}")

        try:
            # Check if the message is from the system/AI
            if origination_number == SYSTEM_NUMBER:
                logger.info("Message originated from the system.")
                # Process system-generated messages here
                process_system_message(message_body)
                return {
                    "statusCode": 200,
                    "body": json.dumps("System message processed"),
                }

            # Step 1: Get active booking based on origination number (guest phone number only)
            booking = BookingService.get_active_booking_by_phone(origination_number)
            if not booking:
                logger.error(f"No active booking found for {origination_number}")
                return {"statusCode": 404, "body": "No active booking found"}

            # Step 2: Get or create a conversation for the booking
            conversation = ConversationService.get_or_create_conversation(booking.id)
            if not conversation:
                logger.error(
                    f"No conversation found or created for booking ID {booking.id}"
                )
                return {"statusCode": 404, "body": "No conversation found"}

            # Step 3: Retrieve guests associated with the booking
            guests = BookingService.get_booking_guests(booking.id)
            if not guests:
                logger.error(f"No guests found for booking ID {booking.id}")
                return {"statusCode": 404, "body": "No guests found"}

            # Step 4: Send the incoming message to all guests except the sender (guests only)
            sender_info = BookingService.get_active_booking_by_phone(
                origination_number
            )  # Store sender info once
            sender_name = (
                sender_info.guest_name if sender_info else "Guest"
            )  # Handle guest name or fallback

            for guest in guests:
                if guest.phone != origination_number:
                    prefixed_message = f"[{sender_name}]: {message_body}"

                    success = MessageService.send_sms(
                        recipient_number=guest.phone,
                        sender_number=SYSTEM_NUMBER,  # System number remains the same
                        message=prefixed_message,
                    )
                    if not success:
                        logger.error(f"Failed to send message to {guest.phone}")

            # Step 5: Process the incoming message and potentially generate a reply
            response_message = MessageService.process_incoming_message(
                origination_number, message_body
            )

            # Step 6: If there's a response from the AI, send it to all participants (guests)
            if response_message:
                for guest in guests:
                    MessageService.send_sms(
                        guest.phone, SYSTEM_NUMBER, response_message
                    )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"statusCode": 500, "body": "Error processing message"}

    return {"statusCode": 200, "body": json.dumps("SMS processed successfully")}


def process_system_message(message_body):
    """
    Handles the message if it's sent by the system/AI.
    Sends the system-generated message to all participants in a conversation.
    """
    logger.info(f"Processing system message: {message_body}")
    # Example: Send a system-wide message
    # Iterate over all active conversations, get participants (guests), and send messages to them
