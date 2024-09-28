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
    Lambda function to handle incoming SMS messages, look up conversation, and send the message to all participants in a group.
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

            # Step 1: Get active booking based on origination number (guest/owner phone number)
            booking = BookingService.get_active_booking_by_phone(origination_number)
            if not booking:
                logger.error(f"No active booking found for {origination_number}")
                return {"statusCode": 404, "body": "No active booking found"}

            # Step 2: Get or create a conversation for the booking
            conversation = ConversationService.get_or_create_conversation(booking["id"])
            if not conversation:
                logger.error(
                    f"No conversation found or created for booking ID {booking['id']}"
                )
                return {"statusCode": 404, "body": "No conversation found"}

            # Step 3: Retrieve participants of the conversation (guests and owner)
            participants = ConversationService.get_conversation_participants(
                conversation["id"]
            )
            if not participants:
                logger.error(
                    f"No participants found for conversation ID {conversation['id']}"
                )
                return {"statusCode": 404, "body": "No participants found"}

            # Step 4: Process the incoming message and potentially generate a reply
            response_message = MessageService.process_incoming_message(
                message_body, origination_number
            )

            # Step 5: Send the incoming message to all participants except the sender
            for participant in participants:
                if participant != origination_number:
                    MessageService.send_sms(
                        participant, origination_number, message_body
                    )

            # Step 6: If there's a response from the AI, send it to all participants
            if response_message:
                for participant in participants:
                    MessageService.send_sms(participant, "AI", response_message)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"statusCode": 500, "body": "Error processing message"}

    return {"statusCode": 200, "body": json.dumps("SMS processed successfully")}


def process_system_message(message_body):
    """
    Handles the message if it's sent by the system/AI.
    Sends the system-generated message to all participants in a conversation.
    """
    # Query active bookings or conversations if needed.
    # Here you could send system-wide announcements or handle the AI response.
    logger.info(f"Processing system message: {message_body}")

    # Example: Send a system-wide message
    # Iterate over all active conversations, get participants, and send messages to them
    # Add your logic to handle system messages here.
