import os
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
        return Tool.from_retrieval(
            grounding.Retrieval(
                grounding.VertexAISearch(
                    datastore=vector_store_id,
                    project=cls.PROJECT_ID,
                    location="us",
                )
            )
        )

    @classmethod
    def prompt(cls, vector_store_id: str, prompt: str) -> str:
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

            response = model.generate_content(
                prompt,
                tools=[tool],
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.2,
                },
            )

            return response.text

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"

    @classmethod
    def prompt_with_context(cls, context: str, prompt: str) -> str:
        """
        Query the model with explicit context

        Args:
            context: The context/documents to ground the response in
            prompt: The text prompt/question for the model
        """
        try:
            model = cls.get_model()
            if not model:
                return "Failed to initialize model"

            # Construct a prompt that includes the context
            full_prompt = f"""Context: {context}

            Question: {prompt}

            Using only the information provided in the context above, please answer the question."""

            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.95,
                },
            )

            return response.text

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"

    @classmethod
    def prompt_with_gcs_documents(cls, bucket_name: str, prefix: str, prompt: str) -> str:
        """
        Query the model using documents from Google Cloud Storage

        Args:
            bucket_name: GCS bucket name
            prefix: Path prefix for relevant JSON documents
            prompt: The text prompt/question for the model
        """
        try:
            # Initialize GCS client
            storage_client = storage.Client(credentials=cls.init_auth())
            bucket = storage_client.bucket(bucket_name)

            # Collect relevant documents
            context_docs = []
            for blob in bucket.list_blobs(prefix=prefix):
                content = blob.download_as_string()
                doc = json.loads(content)
                # Assuming each document has a 'content' field
                if "content" in doc:
                    context_docs.append(doc["content"])

            # Combine documents into context
            combined_context = "\n\n".join(context_docs)

            # Use the context in the prompt
            return cls.prompt_with_context(combined_context, prompt)

        except Exception as e:
            print(f"Error loading GCS documents: {str(e)}")
            return f"Error: {str(e)}"

    @classmethod
    def prompt_with_booking(cls, property_id: str, prompt: str) -> str:
        """
        Query the model using property data from the booking

        Args:
            property_id: ID of the property to query
            prompt: The text prompt/question for the model
        """
        try:
            # Construct the GCS path for the property
            property_path = f"{property_id}.jsonl"

            # Initialize GCS client
            storage_client = storage.Client(credentials=cls.init_auth())
            bucket = storage_client.bucket("amastay_property_data")

            # Get the property document
            blob = bucket.blob(property_path)
            content = blob.download_as_string()

            # Parse JSONL (assuming single line)
            doc = json.loads(content.decode("utf-8").strip())

            # Build comprehensive context from document fields
            context_parts = []

            if doc.get("name"):
                context_parts.append(f"Property Name: {doc['name']}")

            if doc.get("address"):
                context_parts.append(f"Address: {doc['address']}")

            if doc.get("property_information"):
                context_parts.append(f"Property Information: {doc['property_information']}")

            if doc.get("amenities"):
                context_parts.append(f"Amenities: {', '.join(doc['amenities'])}")

            if doc.get("reviews"):
                reviews = "\n".join([f"Review: {review}" for review in doc["reviews"]])
                context_parts.append(f"Guest Reviews:\n{reviews}")

            context = "\n\n".join(context_parts)

            return cls.prompt_with_context(context, prompt)

        except Exception as e:
            print(f"Error loading property data: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":

    user_prompt = "tell me about the property"
    vector_store_id = "amastay-ds-property-text_1735943367196"

    result = LlamaService.prompt_with_booking("36210feb-6a59-46d3-9d5a-c545855e5427", user_prompt)
    print("Model response:", result)
