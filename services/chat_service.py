import json
import boto3
import os

# Load AWS credentials and SageMaker endpoint from environment variables
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT')

# Initialize the SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

def query_model(user_input: str) -> str:
    """
    Sends the user's input to the SageMaker model and returns the model's response.
    """
    payload = {
        "inputs": user_input
    }
    
    try:
        # Call the SageMaker endpoint
        response = sagemaker_runtime.f(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Decode the response body
        response_body = response['Body'].read().decode('utf-8')
        model_response = json.loads(response_body)

        # Handle response, checking if it's a list or dict
        if isinstance(model_response, list):
            return model_response[0].get('generated_text', 'No response received.')
        elif isinstance(model_response, dict):
            return model_response.get('generated_text', 'No response received.')
        else:
            return "Unexpected response format received."

    except Exception as e:
        return f"Error occurred while invoking the model: {str(e)}"
