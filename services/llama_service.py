import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request


class LlamaService:
    """
    A static class for invoking the Llama 3.2 90B Vision Instruct model
    on Vertex AI via REST.
    """

    # Environment variables. In production, set these in your environment or .env file.
    ENDPOINT = os.getenv("GOOGLE_ENDPOINT", "us-central1-aiplatform.googleapis.com")
    REGION = os.getenv("GOOGLE_REGION", "us-central1")
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "amastay")

    # Get the absolute path to the service account file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    @staticmethod
    def get_api_url() -> str:
        """
        Construct the REST endpoint URL for Vertex AI Chat Completions.
        """
        return f"https://{LlamaService.ENDPOINT}/v1beta1/" f"projects/{LlamaService.PROJECT_ID}/locations/{LlamaService.REGION}/" "endpoints/openapi/chat/completions"

    @staticmethod
    def get_default_request_params() -> dict:
        """
        Return default parameters for the request body.
        """
        return {
            "max_tokens": 4000,
            "temperature": 0.4,
            "top_k": 10,
            "top_p": 0.95,
            "n": 1,
            "stream": False,
        }

    @staticmethod
    def get_model():
        return "meta/llama-3.2-90b-vision-instruct-maas"

    @staticmethod
    def build_request_body(image_gcs_path: str, user_text: str) -> dict:
        """
        Build the request payload to send to the model.

        :param image_gcs_path: GCS path of the image (e.g. 'gs://bucket/image.jpg').
        :param user_text: The text prompt/question for the model.
        :param model: The model endpoint identifier.
        :param request_params: A dict of request parameters (max_tokens, temperature, etc.).
                              If None, uses defaults from get_default_request_params().
        :return: Dictionary representing the JSON payload.
        """
        model = LlamaService.get_model()
        request_params = LlamaService.get_default_request_params()

        body = {
            "model": model,
            "stream": request_params.get("stream"),
            "messages": [{"role": "user", "content": [{"image_url": {"url": image_gcs_path}, "type": "image_url"}, {"text": user_text, "type": "text"}]}],
            "max_tokens": request_params.get("max_tokens"),
            "temperature": request_params.get("temperature"),
            "top_k": request_params.get("top_k"),
            "top_p": request_params.get("top_p"),
            "n": request_params.get("n"),
        }
        return body

    @staticmethod
    def get_auth_token() -> str:
        """Get a valid access token using service account credentials"""
        try:
            credentials = service_account.Credentials.from_service_account_file(LlamaService.SERVICE_ACCOUNT_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            return credentials.token
        except FileNotFoundError:
            # Fallback to environment variable if file not found
            return os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
        except Exception as e:
            print(f"Error getting auth token: {str(e)}")
            return ""

    @staticmethod
    def send_request(payload: dict) -> dict:
        """
        Send a POST request to the Vertex AI Chat Completions endpoint.
        """
        url = LlamaService.get_api_url()
        headers = {"Authorization": f"Bearer {LlamaService.get_auth_token()}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        breakpoint()
        print(response)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def parse_response(api_response: dict) -> str:
        """
        Extract text content from the API response.

        :param api_response: The raw JSON response from the model.
        :return: The model's text output as a string.
        """
        try:
            # Typical shape might look like:
            # {
            #   "candidates": [
            #       { "content": "Generated text here..." }
            #   ]
            # }
            candidates = api_response.get("candidates", [])
            if candidates:
                return candidates[0].get("content", "")
            return json.dumps(api_response)  # fallback: return entire JSON if structure unknown
        except Exception as e:
            return f"Failed to parse response: {str(e)}"


# ------------------------------------------------------------------------------
# Example usage:
if __name__ == "__main__":
    # Step 1: Load default parameters (can modify if needed).
    default_params = LlamaService.get_default_request_params()
    # e.g. you can override some of them if you wish:
    # default_params["max_tokens"] = 60
    # default_params["temperature"] = 0.7

    # Step 2: Build the request payload.
    image_path = "gs://amastay/test.png"
    user_prompt = "Whats in this image?"
    request_body = LlamaService.build_request_body(image_gcs_path=image_path, user_text=user_prompt)

    # Step 3: Send the request to the model.
    try:
        response_dict = LlamaService.send_request(request_body)
        # Step 4: Parse and print the result.
        result_text = LlamaService.parse_response(response_dict)
        print("Model response:", result_text)
    except requests.HTTPError as e:
        print("Request failed:", e)
