from uuid import UUID
from models.hf_message_model import HfMessage
from supabase_utils import supabase_client
from models.message_model import Message
from typing import Optional
from datetime import datetime
import json


class MessageService:

    @staticmethod
    def add_message(
        booking_id: str,
        sender_id: Optional[str],
        sender_type: int,
        content: str,
        sms_id: Optional[str] = None,
        question_id: Optional[str] = None,
    ) -> Optional[Message]:
        new_message = {"booking_id": booking_id, "sender_type": sender_type, "content": content}

        # Only add sender_id to the new_message if it's not None
        if sender_id is not None:
            new_message["sender_id"] = sender_id

        # Only add sms_id to the new_message if it's not None
        if sms_id is not None:
            new_message["sms_id"] = sms_id

        # Only add question_id to the new_message if it's not None
        if question_id is not None:
            new_message["question_id"] = question_id

        response = supabase_client.table("messages").insert(new_message).execute()

        if response.data:
            return Message(**response.data[0])  # Return the created message object
        return None

    @staticmethod
    def get_messages_by_booking(booking_id: str, limit: int = 30) -> Optional[list[Message]] | None:
        try:
            response = supabase_client.from_("messages").select("*").eq("booking_id", booking_id).order("created_at", desc=False).limit(limit).execute()
        except Exception as e:
            print(f"Error getting messages by booking: {e}")
            return []

        return [Message(**msg) for msg in response.data] if response.data else []

    @staticmethod
    def get_message_by_sms_id(sms_id: str) -> Optional[Message]:
        response = supabase_client.from_("messages").select("*").eq("sms_id", sms_id).limit(1).execute()

        if response.data:
            return Message(**response.data[0])
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

    @staticmethod
    def get_messages_vertex_format(booking_id: str, limit: int = 100) -> str:
        """
        Get messages for a booking and format them for Vertex AI LLM input.
        Returns JSON string in format required by Vertex AI
        """
        messages = MessageService.get_messages_by_booking(booking_id, limit)

        # Convert messages to Vertex AI format
        formatted_messages = []
        for msg in messages:
            hf_message = HfMessage.from_message(msg)
            formatted_messages.append({"role": hf_message.role, "content": [{"text": content.text, "type": content.type} for content in hf_message.content]})

        content = [{"messages": formatted_messages}]
        return json.dumps(content)
