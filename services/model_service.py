import os
import logging
import traceback
import boto3
from typing import Optional, List, Any
from flask import g
from botocore.exceptions import ClientError
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from models.booking import Booking
from models.guest import Guest
from models.hf_message import HfMessage
from models.property import Property
from models.property_information import PropertyInformation
from services.documents_service import DocumentsService
from services.message_service import MessageService
from services.property_information_service import PropertyInformationService
from services.model_params_service import get_active_model_param
import re

from services.property_service import PropertyService

from botocore.config import Config


class ModelService:
    def __init__(self):

        self.inference_arn = os.getenv("BEDROCK_INFERENCE_ARN")

        # Configure boto3 client with explicit retry config
        config = Config(retries=dict(max_attempts=0), connect_timeout=5, read_timeout=30)  # Disable retries completely

        self.bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1", config=config)

        # Message service to interact with the database
        self.message_service = MessageService()
        self.document_service = DocumentsService()
        self.property_service = PropertyService()
        self.property_information_service = PropertyInformationService()

    def get_conversation_history(self, booking_id: str) -> List[HfMessage]:
        # Fetch conversation history from Supabase
        messages = self.message_service.get_messages_by_booking(booking_id)

        # Handle case where get_messages_by_booking returns None
        if messages is None:
            return []

        # Convert the database messages into HfMessage format for the model
        custom_messages = []
        last_role = None
        for msg in messages:
            current_role = "user" if msg.sender_type == 0 else "assistant"

            # Ensure alternating user/assistant pattern
            if current_role != last_role:
                custom_messages.append(HfMessage.create(role=current_role, text=msg.content))
                last_role = current_role
            else:
                # If same role appears consecutively, combine messages
                if custom_messages:
                    custom_messages[-1].text += f"\n{msg.content}"
                else:
                    custom_messages.append(HfMessage.create(role=current_role, text=msg.content))

        # Ensure the conversation starts with a user message and ends with an assistant message
        if custom_messages and custom_messages[0].role == "assistant":
            custom_messages.insert(0, HfMessage.create(role="user", text="Hello"))
        if custom_messages and custom_messages[-1].role == "user":
            custom_messages.append(HfMessage.create(role="assistant", text="I understand. How can I assist you further?"))

        return custom_messages

    def query_model(
        self,
        booking: Booking,
        property: Property,
        guest: Guest,
        prompt: str,
        message_id: str,
        property_information: Optional[List[PropertyInformation]] = None,
        all_document_text: str = "",
        max_new_tokens: int = 2048,
    ):
        try:

            # Fetch conversation history directly from the database
            conversation_history = self.get_conversation_history(booking.id)
            # Get the active model parameters

            active_model_param = get_active_model_param()

            # Use the prompt from the active model parameters
            system_prompt = [{"text": active_model_param.prompt}]

            # Append property details to system prompt
            property_info_text = ""
            if property_information:
                for info in property_information:
                    property_info_text += f"{info.name}: {info.detail}\n"

            system_prompt[0]["text"] += f". The property details are as follows: Longitude: {property.lat} Latitude: {property.lng} Property Name: {property.name} Address: {property.address} Description: {property.description} Property Information: {property_info_text} Additional Information: {all_document_text}"

            # Trim system prompt if too long
            if len(system_prompt[0]["text"]) > 8000:
                system_prompt[0]["text"] = system_prompt[0]["text"][:8000]

            # Prepare the new user prompt
            new_user_message = HfMessage.create("user", prompt)
            # Add the new user prompt to the conversation history
            conversation_history.append(new_user_message)

            # Prepare payload for the model
            payload = [msg.dict() for msg in conversation_history]

            # Define the system prompt as an array of texts
            response = self.bedrock_client.converse(
                modelId="us.meta.llama3-2-3b-instruct-v1:0",
                messages=payload,
                system=system_prompt,
                inferenceConfig={
                    "maxTokens": 360,
                    "temperature": active_model_param.temperature,
                    "topP": active_model_param.top_p,
                },
                additionalModelRequestFields={},
            )
            breakpoint()
            logging.info(f"AI: Response: {response}")
            # Extract the response text
            if "output" in response and "message" in response["output"] and "content" in response["output"]["message"] and len(response["output"]["message"]["content"]) > 0:
                cleaned_response = self.clean_text(response["output"]["message"]["content"][0]["text"])
            else:
                cleaned_response = "I apologize, but I couldn't generate a proper response."

            if cleaned_response:
                # Save only the new user input and assistant's response directly to the database
                user_message = self.message_service.add_message(
                    booking_id=booking.id,
                    sender_id=guest.id,
                    sender_type=0,
                    content=prompt,
                    sms_id=message_id,
                    question_id=None,
                )
                self.message_service.add_message(
                    booking_id=booking.id,
                    sender_id=None,
                    sender_type=1,
                    content=cleaned_response,
                    sms_id=None,
                    question_id=str(user_message.id),
                )

            # Return the cleaned response
            return {"response": cleaned_response}

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke model'. Reason: {e}")
            return {"error": "I apologize, but I encountered an error while processing your request. " "The error has been logged for further investigation."}

    def clean_document(document: str) -> str:
        pass

    def clean_text(text):
        # # Remove Markdown formatting
        # text = re.sub(r"\*\*|__", "", text)

        # # Remove bullet points and numbering
        # text = re.sub(r"^\s*[\d*-]\s*", "", text, flags=re.MULTILINE)

        # # Remove quotes and parentheses
        # text = re.sub(r"[\"\'()]", "", text)

        # # Remove backslashes
        # text = text.replace("\\n", " ")

        # # Remove extra whitespace and double spaces
        # text = re.sub(r"\s+", " ", text).strip()

        # # Remove period with two spaces followed by another period
        # text = re.sub(r"\. {2}\.", ".", text)

        return text
