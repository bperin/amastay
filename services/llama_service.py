import os
import json
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
    REGION = os.getenv("GOOGLE_REGION", "us-central1")
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "amastay")
    BASE_URL = f"https://{ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi"

    # Service account path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    @classmethod
    def get_client(cls) -> OpenAI:
        """Get an OpenAI client configured for Vertex AI"""
        try:
            credentials = service_account.Credentials.from_service_account_file(cls.SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())

            return OpenAI(api_key=credentials.token, base_url=cls.BASE_URL)  # Token will be used as API key
        except Exception as e:
            print(f"Error creating client: {str(e)}")
            return None

    @classmethod
    def analyze_image(cls, image_gcs_path: str, prompt: str) -> str:
        """
        Analyze an image using the Llama Vision model.

        Args:
            image_gcs_path: GCS path to the image (e.g. 'gs://bucket/image.jpg')
            prompt: The text prompt/question for the model

        Returns:
            The model's response as a string
        """
        try:
            client = cls.get_client()
            if not client:
                return "Failed to initialize client"

            response = client.chat.completions.create(model="meta/llama-3.2-90b-vision-instruct-maas", messages=[{"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_gcs_path}}, {"type": "text", "text": prompt}]}], max_tokens=4000, temperature=0.4, top_p=0.95)

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    image_path = "gs://amastay/test.png"
    user_prompt = "What's in this image?"

    result = LlamaService.analyze_image(image_path, user_prompt)
    print("Model response:", result)
