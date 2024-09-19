import json
import boto3
import os
import logging

# Load environment variables
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_service.log"),
        logging.StreamHandler()
    ]
)

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

class AIService:

    @staticmethod
    def query_model(user_input: str) -> str:
        """
        Sends the user's input to the SageMaker model and returns the model's response.
        """
        payload = {"inputs": f"User Input: {user_input}"}
        
        try:
            # Call SageMaker endpoint with the user input
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType='application/json',
                Body=json.dumps(payload)
            )

            response_body = response['Body'].read().decode('utf-8')
            model_response = json.loads(response_body)

            # Process response based on the format returned by the model
            if isinstance(model_response, list):
                return model_response[0].get('generated_text', 'No response received.')
            elif isinstance(model_response, dict):
                return model_response.get('generated_text', 'No response received.')
            else:
                return "Unexpected response format received."

        except Exception as e:
            logging.error(f"Error invoking SageMaker model: {e}")
            return "Error occurred while invoking the model."
