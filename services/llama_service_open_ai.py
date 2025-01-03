import os
from openai import OpenAI
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import storage
import json


class LlamaService:
    """
    A service for invoking the Llama 3.2 90B Vision Instruct model
    on Vertex AI using the OpenAI-style client.
    """

    # Environment variables
    ENDPOINT = os.getenv("GOOGLE_ENDPOINT", "us-central1-aiplatform.googleapis.com")
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "amastay")
    LOCATION = os.getenv("GOOGLE_REGION", "us-central1")
    BASE_URL = f"https://{ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi"

    # Service account path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    @classmethod
    def get_client(cls) -> OpenAI:
        """Get an OpenAI client configured for Vertex AI"""
        try:
            credentials = service_account.Credentials.from_service_account_file(cls.SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            return OpenAI(api_key=credentials.token, base_url=cls.BASE_URL)
        except Exception as e:
            print(f"Error creating client: {str(e)}")
            return None

    @classmethod
    def get_vector_tool(cls, vector_store_id: str) -> dict:
        """
        Get a vector store tool configuration for Vertex AI Search
        """
        return {"type": "retrieval", "retrieval": {"vertex_ai_search": {"datastore": vector_store_id, "project": cls.PROJECT_ID, "location": "us"}}}

    @classmethod
    def prompt(cls, vector_store_id: str, prompt: str) -> str:
        """
        Query the model with vector store context

        Args:
            vector_store_id: ID of the vector store to use
            prompt: The text prompt/question for the model
        """
        try:
            client = cls.get_client()
            if not client:
                return "Failed to initialize client"

            tool = cls.get_vector_tool(vector_store_id)  #!!! This Tool cannot be passed to openAI

            response = client.chat.completions.create(model="meta/llama-3.2-90b-vision-instruct-maas", messages=[{"role": "user", "content": prompt}], tools=[tool], temperature=0.2, top_p=0.95)

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"

    @classmethod
    def prompt_with_context(cls, context: str, prompt: str) -> str:
        """
        Query the model with explicit context using chat messages

        Args:
            context: The context/documents to ground the response in
            prompt: The text prompt/question for the model
        """
        try:
            client = cls.get_client()
            if not client:
                return "Failed to initialize client"

            # Match the format used in vertex service
            full_prompt = f"""Context: {context}

Question: {prompt}

Using only the information provided in the context above, please answer the question."""

            # Simple message format like vertex
            messages = [{"role": "user", "content": full_prompt}]

            response = client.chat.completions.create(model="meta/llama-3.2-90b-vision-instruct-maas", messages=messages, temperature=0.2, top_p=0.95, max_tokens=4000)

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
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
            # Initialize GCS client
            storage_client = storage.Client(credentials=service_account.Credentials.from_service_account_file(cls.SERVICE_ACCOUNT_PATH))
            bucket = storage_client.bucket("amastay_property_data")

            # Get the property document
            blob = bucket.blob(f"{property_id}.jsonl")
            content = blob.download_as_string()
            doc = json.loads(content.decode("utf-8").strip())

            # Build comprehensive context
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
    prompt = "where is the stove and what model is it?"
    result = LlamaService.prompt_with_booking("36210feb-6a59-46d3-9d5a-c545855e5427", prompt)
    print("Model response:", result)
