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
import boto3
from sagemaker.session import Session


class SageMakerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SageMakerService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize the service with AWS credentials"""
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        if not self.sagemaker_endpoint:
            raise ValueError("SAGEMAKER_ENDPOINT environment variable is required")

        # Get AWS credentials using correct env var names
        self.region_name = os.getenv("SAGEMAKER_REGION")
        self.aws_access_key = os.getenv("SAGEMAKER_ACCESS_KEY")
        self.aws_secret_key = os.getenv("SAGEMAKER_SECRET_ACCESS_KEY")

        if not all([self.region_name, self.aws_access_key, self.aws_secret_key]):
            raise ValueError("SageMaker credentials not properly configured")

        # Debug log environment
        logger.debug(f"Endpoint: {self.sagemaker_endpoint}")
        logger.debug(f"Region: {self.region_name}")
        logger.debug(f"Has SageMaker Access Key: {'SAGEMAKER_ACCESS_KEY' in os.environ}")
        logger.debug(f"Has SageMaker Secret Key: {'SAGEMAKER_SECRET_ACCESS_KEY' in os.environ}")

        # Create runtime client with explicit credentials
        self.runtime_client = boto3.client("sagemaker-runtime", region_name=self.region_name, aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key)

        # Create custom session with our credentials
        sagemaker_session = Session(boto_session=boto3.Session(region_name=self.region_name, aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key))

        # Create predictor with runtime client and custom session
        self.predictor = Predictor(endpoint_name=self.sagemaker_endpoint, serializer=JSONSerializer(), deserializer=JSONDeserializer(), sagemaker_session=sagemaker_session, sagemaker_runtime_client=self.runtime_client)

        self.message_service = MessageService()
        logger.info(f"Initialized SageMaker service with endpoint: {self.sagemaker_endpoint}")

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance"""
        if cls._instance:
            if hasattr(cls._instance, "predictor"):
                del cls._instance.predictor
            cls._instance = None

    def __del__(self):
        """Cleanup when instance is deleted"""
        if hasattr(self, "predictor"):
            del self.predictor

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
