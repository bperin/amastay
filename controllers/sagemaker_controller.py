import os
import json
import boto3
from flask import Blueprint, request, jsonify

# Load environment variables (Access Key, Secret Key, SageMaker endpoint)
SAGEMAKER_ACCESS_KEY = os.getenv("SAGEMAKER_ACCESS_KEY")
SAGEMAKER_SECRET_ACCESS_KEY = os.getenv("SAGEMAKER_SECRET_ACCESS_KEY")
SAGEMAKER_REGION = os.getenv("SAGEMAKER_REGION", "us-east-1")  # default region
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT")

# Initialize boto3 SageMaker client
sagemaker_client = boto3.client(
    "sagemaker-runtime",
    aws_access_key_id=SAGEMAKER_ACCESS_KEY,
    aws_secret_access_key=SAGEMAKER_SECRET_ACCESS_KEY,
    region_name=SAGEMAKER_REGION,
)

# Create a Flask Blueprint for the SageMaker query routes
sagemaker_bp = Blueprint("sagemaker_bp", __name__)


@sagemaker_bp.route("/query_model", methods=["POST"])
def query_model():
    """
    Queries the SageMaker model with user input and context.
    Expects a JSON body with 'input' field containing the user message.
    """
    try:
        # Get the input from the POST request
        data = request.json
        user_input = data.get("input")

        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # Define context with system and user messages
        messages = [
            {"role": "system", "content": "You are Amastay, an AI concierge."},
            {
                "role": "user",
                "content": "My name is Brian. I am the user interacting with you.",
            },
            {"role": "user", "content": user_input},
        ]

        # Prepare the payload for the SageMaker model
        payload = {
            "inputs": json.dumps(messages)
        }  # Ensure messages are sent as a JSON string

        # Send the request to the SageMaker endpoint
        response = sagemaker_client.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType="application/json",
            Body=json.dumps(payload),
        )

        # Decode and parse response
        response_body = response["Body"].read().decode("utf-8")

        # Check if response_body is already a JSON string and parse it
        if isinstance(response_body, str):
            model_response = json.loads(response_body)
        else:
            model_response = response_body

        # Handle response format (assumed as list or dict)
        if isinstance(model_response, list):
            result = model_response[0].get("generated_text", "No response received.")
        elif isinstance(model_response, dict):
            result = model_response.get("generated_text", "No response received.")
        else:
            result = "Unexpected response format received."

        # Return the result to the client
        return jsonify({"response": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
