from uuid import UUID
from supabase_utils import supabase_client
from models.message import Message
from typing import Optional
from datetime import datetime


class MessageService:

    @staticmethod
    def add_message(booking_id: str,
        sender_id: Optional[str],
        sender_type: int,
        content: str,
        question_id: Optional[str] = None,
    ) -> Optional[Message]:
        new_message = {
            "booking_id": booking_id,
            "sender_type": sender_type,
            "content": content,
        }

        # Only add sender_id to the new_message if it's not None
        if sender_id is not None:
            new_message["sender_id"] = sender_id

        # Only add question_id to the new_message if it's not None
        if question_id is not None:
            new_message["question_id"] = question_id

        response = supabase_client.table("messages").insert(new_message).execute()

        if response.data:
            return Message(**response.data[0])  # Return the created message object
        return None

    @staticmethod
    def get_messages_by_booking(booking_id: str, limit: int = 30) -> Optional[list[Message]]:
        response = supabase_client.from_("messages").select("*").eq("booking_id", booking_id).order("created_at", desc=False).limit(limit).execute()

        if response.data:
            return [Message(**msg) for msg in response.data]
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
