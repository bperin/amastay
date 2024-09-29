import json
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Ensure the token is set properly
if hugging_face_hub_token is None:
    raise ValueError(
        "You must provide a valid Hugging Face Hub token in the .env file."
    )

# Hub Model configuration. Update with the correct model ID
hub = {
    "HF_MODEL_ID": "meta-llama/Llama-3.1-8B-Instruct",  # Update to the correct model ID
    "SM_NUM_GPUS": "1",  # Number of GPUs
    "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,  # Use the token from .env
}

# Get the image URI for the model (ensure correct image version)
image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

# Use the correct SageMaker execution role ARN
role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

# Create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
    image_uri=image_uri,
    env=hub,
    role=role_arn,
)

# Deploy the model to SageMaker Inference using an appropriate instance type
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",  # Adjust instance type as per your use case
    container_startup_health_check_timeout=300,  # Timeout in seconds for startup health check
)

# Optionally, save the deployed endpoint name for future use
endpoint_name = predictor.endpoint_name
print(f"Deployed endpoint: {endpoint_name}")

# Example usage: send a test request
response = predictor.predict(
    {
        "inputs": "Hello, can you tell me more about LLaMA?",
    }
)

print(f"Model response: {response}")

# Clean up the endpoint when not needed
# predictor.delete_endpoint()
