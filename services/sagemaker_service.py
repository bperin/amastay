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
from models.sagemaker_response import SageMakerResponse


class SageMakerService:
    def __init__(self):
        # Use the endpoint name, not the ARN
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.region_name = os.getenv("AWS_REGION", "us-east-1")

        # Predictor configuration
        self.predictor = Predictor(endpoint_name=self.sagemaker_endpoint, serializer=JSONSerializer(), deserializer=JSONDeserializer())  # This should be the name, not ARN

        self.message_service = MessageService()

    def get_conversation_history(self, booking_id: str, property: Property, property_information: Optional[List[PropertyInformation]], all_document_text: str = "") -> List[dict]:
        # Create detailed system message with property info
        system_content = "You are a helpful vacation rental assistant. You help guests with their questions about their stay. Keep responses concise and friendly. Prioritize the guest's questions and provide accurate information. Prioritize ##property details## and ##property information## and lastly fall back on any extra ##Additional details##"

        # Add property details
        property_info = f"\n##Property Details:##\nName: {property.name}\nAddress: {property.address}\nDescription: {property.description}\nLocation: Lat {property.lat}, Lng {property.lng}"

        # Add property information if available
        property_info_text = ""
        if property_information:
            property_info_text = "\##Property Information:##\n"
            for info in property_information:
                property_info_text += f"{info.name}: {info.detail}\n"

        # Add any document text
        doc_text = f"\n##Additional Details:##\n{all_document_text}" if all_document_text else ""

        # Combine all system information
        full_system_content = system_content + property_info + property_info_text + doc_text

        # Trim if too long (similar to Bedrock service)
        if len(full_system_content) > 8000:
            full_system_content = full_system_content[:8000]

        # Start with detailed system message
        conversation_history = [{"role": "system", "content": full_system_content}]

        # Fetch conversation history from Supabase
        messages = self.message_service.get_messages_by_booking(booking_id)

        if messages is None:
            return conversation_history

        # Convert database messages to dict format
        for msg in messages:
            conversation_history.append({"role": "user" if msg.sender_type == 0 else "assistant", "content": msg.content})

        return conversation_history

    def query_model(self, booking: Booking, property: Property, guest: Guest, prompt: str, message_id: str, property_information: Optional[List[PropertyInformation]] = None, all_document_text: str = "") -> str:
        try:
            # Get conversation history with property context
            messages = self.get_conversation_history(booking_id=booking.id, property=property, property_information=property_information, all_document_text=all_document_text)

            # Add new prompt
            messages.append({"role": "user", "content": prompt})

            # Prepare payload
            payload = {"messages": messages, "max_new_tokens": 2048}

            # Query model and cast response directly to our model
            raw_sagemaker_response = self.predictor.predict(payload)
            sagemaker_response = SageMakerResponse(**raw_sagemaker_response)
            logger.debug(f"SageMaker response: {sagemaker_response}")

            # Get content directly using model structure
            model_response = sagemaker_response.choices[0].message.content

            # Save messages
            user_message = self.message_service.add_message(booking_id=booking.id, sender_id=guest.id, sender_type=0, content=prompt, sms_id=message_id)

            self.message_service.add_message(booking_id=booking.id, sender_id=None, sender_type=1, content=model_response, sms_id=None, question_id=user_message.id)

            return model_response

        except Exception as e:
            error_message = f"Error querying model: {str(e)}"
            logger.error(error_message)
            logger.error(traceback.format_exc())
            raise
