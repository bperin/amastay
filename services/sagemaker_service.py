import os
import logging
import traceback
from typing import Optional, List

from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.session import Session
import boto3

from models.booking import Booking
from models.property import Property
from models.guest import Guest
from models.property_information import PropertyInformation
from models.sagemaker_response import SageMakerResponse
from services.message_service import MessageService
from services.model_params_service import get_active_model_param

logger = logging.getLogger(__name__)


class SageMakerService:
    predictor: Optional[Predictor] = None
    message_service: Optional[MessageService] = None

    @classmethod
    def initialize(cls):
        """Initialize the service with AWS credentials"""
        if cls.predictor is not None:
            return

        endpoint_name = os.getenv("SAGEMAKER_ENDPOINT")
        logger.info(f"SAGEMAKER_ENDPOINT: {endpoint_name}")
        region_name = os.getenv("SAGEMAKER_REGION")
        aws_access_key = os.getenv("SAGEMAKER_ACCESS_KEY")
        aws_secret_key = os.getenv("SAGEMAKER_SECRET_ACCESS_KEY")

        if not all([endpoint_name, region_name, aws_access_key, aws_secret_key]):
            raise ValueError("SageMaker credentials not properly configured")

        logger.info(f"Initializing SageMaker service with endpoint: {endpoint_name}")

        try:
            # Create custom session with credentials
            sagemaker_session = Session(boto_session=boto3.Session(region_name=region_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key))

            # Create predictor
            cls.predictor = Predictor(endpoint_name=endpoint_name, serializer=JSONSerializer(), deserializer=JSONDeserializer(), sagemaker_session=sagemaker_session)

            cls.message_service = MessageService()
            logger.info("SageMaker service initialized successfully with endpoint: %s", endpoint_name)

        except Exception as e:
            logger.error(f"Failed to initialize SageMaker service: {str(e)}")
            raise

    @classmethod
    def get_conversation_history(cls, booking_id: str, property: Property, property_information: Optional[List[PropertyInformation]], all_document_text: str = "") -> List[dict]:
        """Get conversation history with property context"""
        if cls.predictor is None:
            raise RuntimeError("SageMaker service not initialized")

        try:

            model_params = get_active_model_param()

            system_content = model_params.prompt

            # Create detailed system message
            system_content = "You are a helpful vacation rental assistant. You help guests with " "their questions about their stay. Keep responses concise and friendly. " "Prioritize the guest's questions and provide accurate information. " "Prioritize ##property details## and ##property information## and " "lastly fall back on any extra ##Additional details##"

            # Build context
            property_info = f"\n##Property Details:##\nName: {property.name}\n" f"Address: {property.address}\nDescription: {property.description}\n" f"Location: Lat {property.lat}, Lng {property.lng}"

            property_info_text = ""
            if property_information:
                property_info_text = "\n##Property Information:##\n"
                property_info_text += "\n".join(f"{info.name}: {info.detail}" for info in property_information)

            doc_text = f"\n##Additional Details:##\n{all_document_text}" if all_document_text else ""

            # Combine all system information
            full_system_content = system_content + property_info + property_info_text + doc_text
            if len(full_system_content) > 8000:
                full_system_content = full_system_content[:8000]

            # Build conversation history
            conversation_history = [{"role": "system", "content": full_system_content}]
            messages = cls.message_service.get_messages_by_booking(booking_id)
            if messages:
                conversation_history.extend({"role": "user" if msg.sender_type == 0 else "assistant", "content": msg.content} for msg in messages)

            return conversation_history

        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            raise

    @classmethod
    def query_model(cls, booking: Booking, property: Property, guest: Guest, prompt: str, message_id: str, property_information: Optional[List[PropertyInformation]] = None, all_document_text: str = "") -> str:
        """Query the model with conversation history and context"""
        if cls.predictor is None:
            raise RuntimeError("SageMaker service not initialized")

        try:
            messages = cls.get_conversation_history(booking_id=booking.id, property=property, property_information=property_information, all_document_text=all_document_text)

            messages.append({"role": "user", "content": prompt})
            payload = {"messages": messages, "max_new_tokens": 2048}

            raw_sagemaker_response = cls.predictor.predict(payload)
            sagemaker_response = SageMakerResponse(**raw_sagemaker_response)
            model_response = sagemaker_response.choices[0].message.content

            # Save messages
            user_message = cls.message_service.add_message(booking_id=booking.id, sender_id=guest.id, sender_type=0, content=prompt, sms_id=message_id)

            cls.message_service.add_message(booking_id=booking.id, sender_id=None, sender_type=1, content=model_response, sms_id=None, question_id=user_message.id)

            return model_response

        except Exception as e:
            logger.error(f"Error querying model: {str(e)}\n{traceback.format_exc()}")
            raise
