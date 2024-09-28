import boto3
from botocore.exceptions import ClientError
from supabase_utils import supabase_client


class MessageService:

    @staticmethod
    def send_sms(to_number, message):
        # Initialize AWS Pinpoint client
        client = boto3.client(
            "pinpoint", region_name="your-region"
        )  # Replace with your region

        try:
            response = client.send_messages(
                ApplicationId="your-pinpoint-app-id",  # Replace with your Pinpoint app ID
                MessageRequest={
                    "Addresses": {to_number: {"ChannelType": "SMS"}},
                    "MessageConfiguration": {
                        "SMSMessage": {"Body": message, "MessageType": "TRANSACTIONAL"}
                    },
                },
            )
            print(f"Message sent to {to_number}: {response}")
            return response
        except ClientError as e:
            print(f"Failed to send SMS to {to_number}: {e}")
            return None

    @staticmethod
    def receive_sms(from_number, message):
        # Get the guest or owner by phone number
        guest = (
            supabase_client.table("guests")
            .select("*")
            .eq("phone", from_number)
            .single()
            .execute()
        )
        owner = (
            supabase_client.table("owners")
            .select("*")
            .eq("phone", from_number)
            .single()
            .execute()
        )

        sender_id = None
        sender_type = None

        if guest.data:
            sender_id = guest.data["id"]
            sender_type = "guest"
        elif owner.data:
            sender_id = owner.data["id"]
            sender_type = "owner"

        if sender_id and sender_type:
            # Find the active booking for the guest/owner
            active_booking = BookingService.get_active_booking(sender_id)
            if active_booking:
                # Get or create a conversation for the active booking
                conversation = ConversationService.get_or_create_conversation(
                    active_booking["id"]
                )

                # Add the incoming message to the conversation
                ConversationService.add_message(
                    conversation["id"], sender_id, sender_type, message
                )
            else:
                print("No active booking found for the sender.")
        else:
            print("Sender not found.")
