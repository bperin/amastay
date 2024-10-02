import os
import logging
import traceback
from typing import Optional, List
from flask import g
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from models.hf_message import HfMessage
from services.message_service import MessageService
import re


class ModelService:
    def __init__(self):
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.region_name = os.getenv("AWS_REGION")
        self.endpoint_url = os.getenv("SAGEMAKER_ENDPOINT_URL")

        # Predictor configuration
        self.predictor = Predictor(
            endpoint_name=self.sagemaker_endpoint,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer(),
        )

        # Message service to interact with the database
        self.message_service = MessageService()

    def get_conversation_history(self, booking_id: str) -> List[HfMessage]:
        # Fetch conversation history from Supabase
        messages = self.message_service.get_messages_by_booking(booking_id)

        # Handle case where get_messages_by_booking returns None
        if messages is None:
            return []

        # Convert the database messages into HfMessage format for the model
        custom_messages = [
            HfMessage(
                role="user" if msg.sender_type == 0 else "assistant",
                content=msg.content,
            )
            for msg in messages
        ]
        return custom_messages

    def query_model(self, booking_id: str, prompt: str, max_new_tokens: int = 2048):
        try:
            # Fetch conversation history directly from the database
            conversation_history = self.get_conversation_history(booking_id)

            # Add the new user prompt
            conversation_history.append(HfMessage(role="user", content=prompt))
            print(f"Conversation History: {conversation_history}")

            # Prepare payload for the model
            payload = {
                "messages": [msg.dict() for msg in conversation_history],
                "max_new_tokens": max_new_tokens,
            }
            print(f"Payload for session {booking_id}: {payload}")

            # Query the model
            response = self.predictor.predict(payload)

            # Extract and clean the response from the model
            cleaned_response = self.clean_text(
                response["choices"][0]["message"]["content"]
            )

            # Save the user's input and assistant's response directly to the database
            user_message = self.message_service.add_message(
                booking_id=booking_id,
                sender_id=g.user_id,
                sender_type=0,
                content=prompt,
                question_id=None,
            )
            self.message_service.add_message(
                booking_id=booking_id,
                sender_id=None,
                sender_type=1,
                content=cleaned_response,
                question_id=str(user_message.id),
            )

            return cleaned_response

        except Exception as e:
            error_message = f"Error querying model: {str(e)}"
            logging.exception(error_message)
            print(error_message)
            traceback.print_exc()
            return (
                "I apologize, but I encountered an error while processing your request. "
                "The error has been logged for further investigation."
            )

    @staticmethod
    def clean_text(text):
        # Remove Markdown formatting
        text = re.sub(r"\*\*|__", "", text)

        # Remove bullet points and numbering
        text = re.sub(r"^\s*[\d*-]\s*", "", text, flags=re.MULTILINE)

        # Remove quotes and parentheses
        text = re.sub(r"[\"\'()]", "", text)

        # Remove backslashes
        text = text.replace("\\n", " ")

        # Remove extra whitespace and double spaces
        text = re.sub(r"\s+", " ", text).strip()

        # Remove period with two spaces followed by another period
        text = re.sub(r"\. {2}\.", ".", text)

        return text
