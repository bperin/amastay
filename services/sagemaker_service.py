import os
import re
import logging
import traceback
from typing import Optional, List, TYPE_CHECKING
from venv import logger

from flask import g
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from models.hf_message import HfMessage
from services.message_service import MessageService
from models.booking import Booking
from models.property import Property
from models.guest import Guest
from models.property_information import PropertyInformation


class SageMakerService:
    def __init__(self):
        # Use the endpoint name, not the ARN
        self.sagemaker_endpoint = "huggingface-pytorch-tgi-inference-2024-11-07-06-05-45-629"
        self.region_name = os.getenv("AWS_REGION", "us-east-1")

        # Predictor configuration
        self.predictor = Predictor(endpoint_name=self.sagemaker_endpoint, serializer=JSONSerializer(), deserializer=JSONDeserializer())  # This should be the name, not ARN

        self.message_service = MessageService()

    def get_conversation_history(self, booking_id: str) -> List[dict]:
        # Fetch conversation history from Supabase
        messages = self.message_service.get_messages_by_booking(booking_id)

        if messages is None:
            return []

        # Start with system message
        conversation_history = [{"role": "system", "content": "You are a helpful assistant for managing vacation rentals."}]

        # Add conversation messages in simple format
        for msg in messages:
            conversation_history.append({"role": "user" if msg.sender_type == 0 else "assistant", "content": msg.content})

        return conversation_history

    def query_model(self, booking: "Booking", property: "Property", guest: "Guest", prompt: str, message_id: str, property_information: Optional[List[PropertyInformation]] = None, all_document_text: str = "") -> str:
        try:
            # Get conversation history
            conversation_history = self.get_conversation_history(booking.id)
            logging.info(f"Conversation history: {conversation_history}")

            # Prepare payload - simplify to match deploy_model.py format
            payload = {"messages": conversation_history + [{"role": "user", "content": prompt}]}

            logging.info(f"Sending payload to SageMaker: {payload}")

            try:
                response = self.predictor.predict(payload)
                logging.info(f"Raw response from SageMaker: {response}")
            except Exception as predict_error:
                logging.error(f"Prediction error: {str(predict_error)}")
                logging.error(f"Prediction error type: {type(predict_error)}")
                raise
            # Handle Llama model's response format
            if isinstance(response, str):
                cleaned_response = response

            elif isinstance(response, dict):
                # Get the actual response text based on Llama's format
                if "generation" in response:
                    cleaned_response = response["generation"]
                elif "content" in response:
                    cleaned_response = response["content"]
                else:
                    logging.error(f"Unexpected response format: {response}")
                    # Default to full response if structure is unknown
                    cleaned_response = str(response)
            else:
                logging.error(f"Unknown response type: {type(response)}")
                cleaned_response = str(response)

            # Save messages
            user_message = self.message_service.add_message(booking_id=booking.id, sender_id=guest.id, sender_type=0, content=prompt, sms_id=message_id)

            self.message_service.add_message(booking_id=booking.id, sender_id=None, sender_type=1, content=cleaned_response, sms_id=None, question_id=str(user_message.id))

            return cleaned_response

        except Exception as e:
            logging.error(f"Full error details: {str(e)}")
            logging.error(f"Stack trace: {traceback.format_exc()}")
            raise
