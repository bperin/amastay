import json
import time
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from dotenv import load_dotenv
import os


def generate_unique_name(base_name):
    """Generate a unique name with timestamp"""
    timestamp = int(time.time())
    return f"{base_name}-{timestamp}"


# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Ensure the token is set properly
if hugging_face_hub_token is None:
    raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

# Hub Model configuration
hub = {
    "HF_MODEL_ID": "meta-llama/Llama-3.2-3B-Instruct",
    "SM_NUM_GPUS": "1",  # Number of GPUs to use
    "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,
    "MESSAGES_API_ENABLED": "true",
}

# Get the image URI for the model
image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

# Use the correct SageMaker execution role ARN
role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

# Create Hugging Face Model Class
huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn, name=generate_unique_name("llama-3b"))  # Add unique name for model

# Create unique endpoint name
endpoint_name = generate_unique_name("llama-3b-endpoint")

# Update instance type based on GPU requirements
predictor = huggingface_model.deploy(initial_instance_count=1, instance_type="ml.g5.12xlarge", container_startup_health_check_timeout=300, endpoint_name=endpoint_name)

print(f"Deployed endpoint: {endpoint_name}")

# Send request to the deployed model endpoint
response = predictor.predict(
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is deep learning?"},
        ]
    }
)

print(response)

# Ask if user wants to clean up
cleanup = input("\nDo you want to clean up the endpoint and configuration? (y/N): ")
if cleanup.lower() == "y":
    print("Cleaning up resources...")
    predictor.delete_endpoint()
