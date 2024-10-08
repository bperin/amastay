import os
import logging
import traceback
import boto3
from typing import Optional, List, Any
from flask import g
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from models.hf_message import HfMessage
from services.documents_service import DocumentsService
from services.message_service import MessageService
import re


class ModelService:
    def __init__(self):
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.region_name = os.getenv("AWS_REGION")
        self.endpoint_url = os.getenv("SAGEMAKER_ENDPOINT_URL")
        self.inference_arn = "arn:aws:bedrock:us-east-1:422220778159:inference-profile/us.meta.llama3-2-3b-instruct-v1:0"

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

    def get_documents_by_booking(self, booking_id: str) -> List[Any]:
        # Fetch documents related to the booking
        docs = self.document_service.get_documents_by_booking_id(booking_id)
        return docs

    def query_model(self, booking_id: str, prompt: str, max_new_tokens: int = 2048):
        try:
            # Fetch conversation history directly from the database
            conversation_history = self.get_conversation_history(booking_id)

            system_prompt = [
                {
                    "text": "You are an expert question an anaswer chat assistanted that gives clear and concise responses about short term rentals. You are provided with the following documents which may help you answer the users question. If you cannot answer the users question, please ask for more information"
                }
            ]
            # Fetch documents related to the booking
            document_urls = self.get_documents_by_booking(booking_id)
            for url in document_urls:
                document_content = self.document_service.read_document(url)
                if document_content:
                    system_prompt.append({"text": document_content})

            # Add the new user prompt
            conversation_history.append(HfMessage.create("user", prompt))
            print(f"Conversation History: {conversation_history}")

            # Prepare payload for the model
            payload = [msg.dict() for msg in conversation_history]
            print(f"Payload for session {booking_id}: {payload}")

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
