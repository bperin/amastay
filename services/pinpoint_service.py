import logging
from datetime import datetime
import os
from typing import Optional
from supabase_utils import supabase_client
import boto3


class PinpointService:

    @staticmethod
    def send_sms(phone_number: str, sender_number: str, message_content: str) -> Optional[str]:
        """
        Sends an SMS message via AWS Pinpoint and returns the SMS message ID.

        Args:
            phone_number (str): The recipient's phone number.
            sender_number (str): The system phone number.
            message_content (str): The content of the SMS. 

        Returns:
            Optional[str]: The SMS message ID if successful, None otherwise.
        """
        try:
            pinpoint = boto3.client("pinpoint", aws_access_key_id=os.getenv("PINPOINT_ACCESS_KEY"), aws_secret_access_key=os.getenv("PINPOINT_SECRET_ACCESS_KEY"), region_name="us-east-1")  # Assuming the region is us-east-1, adjust if different

            response = pinpoint.send_messages(
                ApplicationId=os.getenv("PINPOINT_PROJECT_ID"),
                MessageRequest={
                    "Addresses": {phone_number: {"ChannelType": "SMS"}},
                    "MessageConfiguration": {
                        "SMSMessage": {
                            "Body": message_content,
                            "MessageType": "TRANSACTIONAL",
                            "OriginationNumber": sender_number,
                        }
                    },
                },
            )

            if response["MessageResponse"]["Result"][phone_number]["StatusCode"] == 200:
                return response["MessageResponse"]["Result"][phone_number]["MessageId"]
            else:
                logging.error(f"Failed to send SMS to {phone_number}")
                return None

        except Exception as e:
            logging.error(f"Error sending SMS: {str(e)}")
            return None

        # No retry logic implemented. If it fails, it fails.

    @staticmethod
    def update_message_sms_id(message_id: str, sms_id: str) -> bool:
        """
        Updates the 'sms_id' of a message in the database.

        Args:
            message_id (str): The ID of the message to update.
            sms_id (str): The SMS message ID returned by AWS Pinpoint.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        response = supabase_client.table("messages").update({"sms_id": sms_id, "updated_at": datetime.utcnow()}).eq("id", message_id).execute()

        return response.status_code == 200
