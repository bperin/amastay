import os
import logging
import traceback
import boto3
from typing import Optional, List, Any
from flask import g
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
import re

from services.property_service import PropertyService


class ModelService:
    def __init__(self):
        # self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        # self.region_name = os.getenv("AWS_REGION")
        # self.endpoint_url = os.getenv("SAGEMAKER_ENDPOINT_URL")
        # TODO: Replace this hardcoded ARN with an environment variable
        self.inference_arn = os.getenv(
            "BEDROCK_INFERENCE_ARN",
            "arn:aws:bedrock:us-east-1:422220778159:inference-profile/us.meta.llama3-2-3b-instruct-v1:0",
        )

        self.bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
        # self.sagemaker_client = boto3.client("sagemaker", region_name=self.region_name)

        # Create SageMaker Runtime client
        # self.sagemaker_runtime = boto3.client(
        #     "sagemaker-runtime", region_name=self.region_name
        # )

        # Predictor configuration
        # self.predictor = Predictor(
        #     endpoint_name=self.sagemaker_endpoint,
        #     serializer=JSONSerializer(),
        #     deserializer=JSONDeserializer(),
        # )

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
                custom_messages.append(
                    HfMessage.create(role=current_role, text=msg.content)
                )
                last_role = current_role
            else:
                # If same role appears consecutively, combine messages
                if custom_messages:
                    custom_messages[-1].text += f"\n{msg.content}"
                else:
                    custom_messages.append(
                        HfMessage.create(role=current_role, text=msg.content)
                    )

        # Ensure the conversation starts with a user message and ends with an assistant message
        if custom_messages and custom_messages[0].role == "assistant":
            custom_messages.insert(0, HfMessage.create(role="user", text="Hello"))
        if custom_messages and custom_messages[-1].role == "user":
            custom_messages.append(
                HfMessage.create(
                    role="assistant", text="I understand. How can I assist you further?"
                )
            )

        return custom_messages

    def query_model(
        self,
        booking: Booking,
        property: Property,
        guest: Guest,
        prompt: str,
        property_information: Optional[List[PropertyInformation]] = None,
        all_document_text: str = "",
        max_new_tokens: int = 2048,
    ):
        try:

            # Fetch conversation history directly from the database
            conversation_history = self.get_conversation_history(booking.id)

            system_prompt = [
                {
                    "text": f"You are an expert question and answer chat assistant that gives clear and concise responses about short term rentals. You are provided with the following documents and property information which may help you answer the user's question. If you cannot answer the user's question, please ask for more information. The property details are as follows:\n\nProperty Name: {property.name}\nAddress: {property.address}\nDescription: {property.description}"
                }
            ]

            # Add property information to system prompt
            if property_information:
                for info in property_information:
                    system_prompt.append(
                        {"text": f"{info.name}, Detail: {info.detail}"}
                    )

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
                inferenceConfig={"maxTokens": 360, "temperature": 0.7, "topP": 0.9},
                additionalModelRequestFields={},
            )

            # Extract the response text
            if (
                "output" in response
                and "message" in response["output"]
                and "content" in response["output"]["message"]
                and len(response["output"]["message"]["content"]) > 0
            ):
                cleaned_response = self.clean_text(
                    response["output"]["message"]["content"][0]["text"]
                )
            else:
                cleaned_response = (
                    "I apologize, but I couldn't generate a proper response."
                )

            if cleaned_response:
                # Save only the new user input and assistant's response directly to the database
                user_message = self.message_service.add_message(
                    booking_id=booking.id,
                    sender_id=guest.id,
                    sender_type=0,
                    content=prompt,
                    question_id=None,
                )
                self.message_service.add_message(
                    booking_id=booking.id,
                    sender_id=None,
                    sender_type=1,
                    content=cleaned_response,
                    question_id=str(user_message.id),
                )

            # Return the cleaned response
            return {"response": cleaned_response}

        except Exception as e:
            error_message = f"Error querying model: {str(e)}"
            logging.exception(error_message)
            print(error_message)
            traceback.print_exc()
            return {
                "error": "I apologize, but I encountered an error while processing your request. "
                "The error has been logged for further investigation."
            }

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
