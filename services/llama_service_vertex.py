import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from vertexai.preview.generative_models import (
    GenerativeModel,
    Tool,
    grounding,
)
import vertexai
import json
from google.cloud import storage

from models.hf_message_model import HfMessage
from models.message_model import Message
from services.message_service import MessageService


class LlamaService:
    """
    A service for invoking the Llama 3.2 90B Vision Instruct model
    on Vertex AI using the native SDK.
    """

    # Environment variables
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "amastay")
    LOCATION = os.getenv("GOOGLE_REGION", "us-central1")

    # Service account path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    @classmethod
    def init_auth(cls):
        """Initialize authentication with service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(cls.SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            return credentials
        except Exception as e:
            print(f"Error initializing auth: {str(e)}")
            return None

    @classmethod
    def get_model(cls) -> GenerativeModel:
        """Get a Vertex AI generative model"""
        try:
            credentials = cls.init_auth()
            if not credentials:
                return None

            vertexai.init(project=cls.PROJECT_ID, location=cls.LOCATION, credentials=credentials)
            return GenerativeModel("publishers/meta/models/llama-3.2-90b-vision-instruct-maas")
        except Exception as e:
            print(f"Error creating model: {str(e)}")
            return None

    @classmethod
    def get_vector_tool(cls, vector_store_id: str) -> Tool:
        """
        Get a vector store tool for the Vertex AI Vector Store API
        """
        return Tool.from_retrieval(grounding.Retrieval(grounding.VertexAISearch(datastore=vector_store_id, project=cls.PROJECT_ID, location="us")))

    @classmethod
    def prompt(cls, vector_store_id: str, booking_id: str, prompt: str) -> str:
        """
        Query the model with vector store context

        Args:
            vector_store_id: ID of the vector store to use
            prompt: The text prompt/question for the model
        """
        try:
            model = cls.get_model()
            if not model:
                return "Failed to initialize model"

            tool = cls.get_vector_tool(vector_store_id)
            logging.info(f"Querying model for booking: {booking_id} with prompt: {prompt}")
            # Pass prompt to get_messages_vertex_format
            content = MessageService.get_messages_vertex_format(booking_id=booking_id)
            print(content)
            response = model.generate_content(
                content,
                tools=[tool],
                generation_config={
                    "max_output_tokens": 4000,
                    "temperature": 0.5,
                    "top_p": 0.5,
                },
            )
            if response.text:
                # adding assistant message to DB
                MessageService.add_message(booking_id=booking_id, sender_id=None, sender_type=0, content=response.text)
                return response.text
            else:
                logging.error(f"No response from model: {response}")
                return "No response from model"

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":

    user_prompt = "tel me a fun activity around the property"
    vector_store_id = "amastay-ds-property-text_1735943367196"
    property_id = "36210feb-6a59-46d3-9d5a-c545855e5427"
    booking_id = "9f175302-de9f-421e-8e85-3c5780075875"
    result = LlamaService.prompt(vector_store_id, booking_id, user_prompt)
    print("Model response:", result)
