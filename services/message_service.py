from supabase_utils import supabase_client
from models.message import Message
from typing import Optional
from datetime import datetime


class MessageService:

    @staticmethod
    def add_message(
        booking_id: str, sender_id: str, sender_type: int, content: str
    ) -> Optional[Message]:
        new_message = {
            "booking_id": booking_id,
            "sender_id": sender_id,
            "sender_type": sender_type,
            "content": content,
        }

        response = supabase_client.table("messages").insert(new_message).execute()

        if response.data:
            return Message(**response.data[0])  # Return the created message object
        return None

    @staticmethod
    def get_messages_by_booking(
        booking_id: str, limit: int = 15
    ) -> Optional[list[Message]]:
        response = (
            supabase_client.table("messages")
            .select("*")
            .eq("booking_id", booking_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        if response.data:
            return [Message(**msg) for msg in response.data]
        return None

    @staticmethod
    def get_booking_id_by_sms_id(sms_id: str) -> Optional[str]:

        response = (
            supabase_client.table("messages")
            .select("booking_id")
            .eq("sms_id", sms_id)
            .single()
            .execute()
        )

        if response.data:
            return response.data["booking_id"]

        return None

    @staticmethod
    def update_message_sms_id(message_id: str, sms_id: str) -> bool:

        response = (
            supabase_client.table("messages")
            .update(
                {
                    "sms_id": sms_id,
                }
            )
            .eq("id", message_id)
            .execute()
        )

        return response.status_code == 200
