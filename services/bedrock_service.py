import os
import logging
import boto3
from typing import Optional, List
from botocore.config import Config
from models.booking import Booking
from models.guest import Guest
from models.hf_message import HfMessage
from models.property import Property
from models.property_information import PropertyInformation
from models.system_prompt import SystemPrompt
from services import booking_service, guest_service, property_service
from services.message_service import MessageService
from services.model_params_service import get_active_model_param

logger = logging.getLogger(__name__)


class BedrockService:
    bedrock_client = None
    message_service = MessageService()

    @classmethod
    def initialize(cls):
        """Initialize Bedrock client with AWS credentials"""
        if cls.bedrock_client is not None:
            return

        # Get AWS credentials from environment
        region_name = os.getenv("SAGEMAKER_REGION")
        aws_access_key = os.getenv("SAGEMAKER_ACCESS_KEY")
        aws_secret_key = os.getenv("SAGEMAKER_SECRET_ACCESS_KEY")

        if not all([aws_access_key, aws_secret_key]):
            raise ValueError("Bedrock credentials not properly configured")

        config = Config(retries=dict(max_attempts=3), connect_timeout=5, read_timeout=30)

        # Create boto3 client with credentials
        cls.bedrock_client = boto3.client("bedrock-runtime", region_name=region_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, config=config)

    @classmethod
    def get_conversation_history(cls, booking: Booking) -> List[HfMessage]:
        """Get conversation history with property context"""
        if cls.bedrock_client is None:
            raise RuntimeError("Bedrock service not initialized")
        conversation_history = []
        # Add message history
        messages = cls.message_service.get_messages_by_booking(booking.id)
        if messages:
            for msg in messages:
                role = "user" if msg.sender_type == 0 else "assistant"
                conversation_history.append(HfMessage.create(role=role, content=msg.content))

        return conversation_history

    @classmethod
    def get_basic_query(cls, prompt: str):
        messages = HfMessage.create(role="user", content=prompt)
        payload = [msg.dict() for msg in messages]
        response = cls.bedrock_client.converse(modelId="us.meta.llama3-2-3b-instruct-v1:0", messages=payload, inferenceConfig={"maxTokens": 360, "temperature": 0.5, "topP": 0.5})
        return response["message"]["content"][0]["text"]

    @classmethod
    def get_system_prompt(cls, booking: Booking, property: Property, Guest: Guest, document_text: Optional[str] = None) -> str:

        model_params = get_active_model_param()

        property_information = ""
        # all_document_text = document_service.get_all_document_text_by_property_id(property_id)
        # Build system prompt with context
        system_content = model_params.prompt
        property_info = f"\n#Property Details:#\nName: {property.name}\n" f"Address: {property.address}\nDescription: {property.description}\n" f"Location at ({property.lat}, {property.lng})"
        property_info += f"\n#Booking Details:#\nCheck-in: {booking.check_in}\nCheck-out: {booking.check_out}\n"

        property_info_text = ""
        if property_information:
            property_info_text = "\n#Property Information:#\n"
            property_info_text += "\n".join(f"{info.name}: {info.detail}" for info in property_information)

        doc_text = f"\n#Property documents#\n{document_text}" if document_text else ""

        # Combine all system information
        full_system_content = system_content + property_info + property_info_text + doc_text
        if len(full_system_content) > 8000:
            full_system_content = full_system_content[:8000]

        return full_system_content

    @classmethod
    def query_model(
        cls,
        booking: Booking,
        property: Property,
        guest: Guest,
        prompt: str,
        message_id: str,
        document_text: Optional[str] = None,
    ) -> str:
        """Query the Bedrock model with conversation history and context"""
        if cls.bedrock_client is None:
            raise RuntimeError("Bedrock service not initialized")

        try:
            messages = cls.get_conversation_history(booking)

            # Add the new user message
            messages.append(HfMessage.create(role="user", content=prompt))

            # Convert messages to payload format
            payload = [msg.dict() for msg in messages]

            # Get model parameters
            model_params = get_active_model_param()
            raw_system_prompt = cls.get_system_prompt(booking, property, guest, document_text)
            system_prompt = SystemPrompt.create(raw_system_prompt)

            # Query Bedrock
            response = cls.bedrock_client.converse(
                system=system_prompt,
                modelId="us.meta.llama3-2-3b-instruct-v1:0",
                messages=payload,
                inferenceConfig={
                    "maxTokens": 360,
                    "temperature": model_params.temperature,
                    "topP": model_params.top_p,
                },
            )

            # Extract and clean response
            if "output" in response:
                model_response = response["output"]["message"]["content"][0]["text"]
            else:
                model_response = "I apologize, but I couldn't generate a proper response."

            # Save messages
            user_message = cls.message_service.add_message(booking_id=booking.id, sender_id=guest.id, sender_type=0, content=prompt, sms_id=message_id)

            cls.message_service.add_message(booking_id=booking.id, sender_id=None, sender_type=1, content=model_response, sms_id=None, question_id=str(user_message.id))

            return model_response

        except Exception as e:
            logger.error(f"Error querying model: {str(e)}")
            return {"error": "I apologize, but I encountered an error while processing your request. " "The error has been logged for further investigation."}
