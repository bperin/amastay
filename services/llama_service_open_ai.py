import os
from openai import OpenAI
from google.oauth2 import service_account
from google.auth.transport.requests import Request


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

            response = client.chat.completions.create(model="meta/llama-3.2-90b-vision-instruct-maas", messages=[{"role": "user", "content": prompt}], tools=[tool], temperature=0.4, top_p=0.95)

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    test_cases = [{"prompt": "does this place have a pool?", "store_id": "property-test_1735687819569"}, {"prompt": "what are the amenities?", "store_id": "property-test_1735687819569"}]

    for case in test_cases:
        print(f"\nTesting prompt: '{case['prompt']}'")
        print(f"Using store ID: {case['store_id']}")
        result = LlamaService.prompt(case["store_id"], case["prompt"])
        print("Model response:", result)
        print("-" * 80)
