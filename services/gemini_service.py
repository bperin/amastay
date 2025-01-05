import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from vertexai.preview.generative_models import (
    GenerativeModel,
    Tool,
    grounding,
)
import vertexai


class GeminiService:
    """
    A service for invoking the Gemini 2.0 Flash Exp model
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
            return GenerativeModel("gemini-1.5-flash-001")
        except Exception as e:
            print(f"Error creating model: {str(e)}")
            return None

    @classmethod
    def get_vector_tool(cls, vector_store_id: str) -> Tool:
        datastore_path = f"projects/{cls.PROJECT_ID}/locations/{cls.LOCATION}/collections/default_collection/dataStores/{vector_store_id}"
        print(f"Using datastore path: {datastore_path}")  # Debug print

        try:
            return Tool.from_retrieval(
                grounding.Retrieval(
                    grounding.VertexAISearch(
                        datastore=vector_store_id,
                        project=cls.PROJECT_ID,
                        location="us",
                    )
                )
            )
        except Exception as e:
            print(f"Error creating vector tool: {str(e)}")
            return None

    @classmethod
    def prompt(cls, vector_store_id: str, prompt: str) -> str:
        """
        Query the model with vector store context

        Args:
            vector_store_id: ID of the vector store to use
            prompt: The text prompt/question for the model

        Returns:
            str: Model response or error message
        """
        try:
            model = cls.get_model()
            if not model:
                return "Failed to initialize model"

            tool = cls.get_vector_tool(vector_store_id)

            # Add safety parameters and temperature
            response = model.generate_content(
                prompt,
                tools=[tool],
                generation_config={"max_output_tokens": 400, "temperature": 0.2, "top_p": 0.2},
            )

            if response.candidates[0].finish_reason == "SAFETY":
                return "Response was filtered due to safety concerns"

            return response.text

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    user_prompt = "where can i park my car"
    vector_store_id = "amastay-ds-property-text_1735943367196"

    result = GeminiService.prompt(vector_store_id, user_prompt)
    print("Model response:", result)
