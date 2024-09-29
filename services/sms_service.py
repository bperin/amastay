import os
from typing import Optional
from supabase_utils import supabase_client
from services.booking_service import BookingService
from models.message import Message


class SmsService:

    @staticmethod
    def notify_guests_by_message(message: Message) -> None:
        """
        Retrieves the guests associated with the booking in the message and sends an SMS to all guests.
        Args:
            message (Message): The message object containing the booking and content information.
        """
        # Step 1: Get guests by booking ID
        guests = BookingService.get_booking_guests(message.booking_id)

        if not guests:
            print(f"No guests found for booking ID {message.booking_id}")
            return

        # Step 2: Notify all guests except the sender
        for guest in guests:
            if guest.id != message.sender_id:
                # Send the SMS and get the SMS ID
                sms_id = SmsService.send_sms(
                    guest.phone, os.getenv("SYSTEM_PHONE_NUMBER"), message.content
                )

                if sms_id:
                    # Step 3: Update the message with the SMS ID after successfully sending the SMS
                    SmsService.update_message_sms_id(message.id, sms_id)
                else:
                    print(f"Failed to send SMS to {guest.phone}")

    @staticmethod
    def send_sms(
        phone_number: str, sender_number: str, message_content: str
    ) -> Optional[str]:
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
            response = supabase_client.pinpoint.send_messages(
                ApplicationId=os.getenv("PINPOINT_APP_ID"),
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
                print(f"Failed to send SMS to {phone_number}")
                return None

        except Exception as e:
            print(f"Error sending SMS: {e}")
            return None

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
        response = (
            supabase_client.table("messages")
            .update({"sms_id": sms_id, "updated_at": datetime.utcnow()})
            .eq("id", message_id)
            .execute()
        )

        return response.status_code == 200
