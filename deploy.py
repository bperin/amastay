import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv('HUGGING_FACE_HUB_TOKEN')

# Ensure the token is set properly
assert hugging_face_hub_token is not None, "You must provide a valid Hugging Face Hub token in the .env file."

# Hub Model configuration. https://huggingface.co/models
hub = {
    'HF_MODEL_ID': 'meta-llama/Meta-Llama-3.1-8B-Instruct',  # The LLaMA model
    'SM_NUM_GPUS': json.dumps(1),  # Number of GPUs
    'HUGGING_FACE_HUB_TOKEN': hugging_face_hub_token  # Use the token from .env
}

# Get the image URI for the model
image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

# Use the correct SageMaker execution role ARN
role_arn = 'arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole'

# Create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
    image_uri=image_uri,
    env=hub,
    role=role_arn,  # Use the correct role ARN
)

# Deploy the model to SageMaker Inference using the smaller `ml.g5.xlarge` instance
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",  # Use a smaller GPU instance for testing
    container_startup_health_check_timeout=300,
)

# Example usage: send a test request
response = predictor.predict({
    "inputs": "Hello, can you tell me more about LLaMA?",
})

print(f"Model response: {response}")
