import os
import logging
from typing import Optional
from openai import OpenAI
from google.oauth2 import service_account
from google.auth.transport.requests import Request


class LlamaImageService:
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

    PROPERTY_PHOTO_PROMPT = """
    Analyze this property photo in detail. Focus on:
    1. Room/area type and purpose
    2. Key features and amenities visible
    3. Design elements and finishes
    4. Notable architectural details
    5. Overall condition and quality
    Be specific but concise. Format as a clear, descriptive paragraph.
    """

    @classmethod
    def get_client(cls) -> Optional[OpenAI]:
        """Get an OpenAI client configured for Vertex AI"""
        try:
            credentials = service_account.Credentials.from_service_account_file(cls.SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())

            client = OpenAI(api_key=credentials.token, base_url=cls.BASE_URL)
            logging.info("Successfully created Llama Vision client")
            return client

        except Exception as e:
            logging.error(f"Error creating Llama Vision client: {str(e)}")
            return None

    @classmethod
    async def analyze_image(cls, gcs_uri: str) -> str:
        """
        Analyze a property photo using the Llama Vision model.

        Args:
            gcs_uri: GCS path to the image (e.g. 'gs://bucket/image.jpg')

        Returns:
            Detailed description of the property photo
        """
        try:
            client = cls.get_client()
            if not client:
                logging.error("Failed to initialize Llama Vision client")
                return "Error: Failed to initialize image analysis service"

            logging.info(f"Analyzing image: {gcs_uri}")
            response = client.chat.completions.create(model="meta/llama-3.2-90b-vision-instruct-maas", messages=[{"role": "user", "content": [{"type": "image_url", "image_url": {"url": gcs_uri}}, {"type": "text", "text": cls.PROPERTY_PHOTO_PROMPT}]}], max_tokens=4000, temperature=0.2, top_p=0.95, stream=False)

            description = response.choices[0].message.content
            logging.info(f"Successfully analyzed image: {gcs_uri[:100]}...")
            return description

        except Exception as e:
            error_msg = f"Error analyzing image {gcs_uri}: {str(e)}"
            logging.error(error_msg)
            return f"Error: Failed to analyze image - {str(e)}"


if __name__ == "__main__":
    # Test the service
    test_image = "gs://amastay_property_photos/test/sample.jpg"
    import asyncio

    async def test():
        result = await LlamaImageService.analyze_image(test_image)
        print("Analysis result:", result)

    asyncio.run(test())
