import json
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv('HUGGING_FACE_HUB_TOKEN')

# Ensure the token is set properly
if hugging_face_hub_token is None:
    raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

# Hub Model configuration. https://huggingface.co/models
hub = {
    'HF_MODEL_ID': 'meta-llama/Llama-3.2-3B-Instruct',  # Ensure this is the correct model ID
    'SM_NUM_GPUS': '1',  # Number of GPUs, no need to json.dumps here
    'HUGGING_FACE_HUB_TOKEN': hugging_face_hub_token  # Use the token from .env
}

# Get the image URI for the model (ensure correct image version)
image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

# Use the correct SageMaker execution role ARN
role_arn = 'arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole'

# Create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
    image_uri=image_uri,
    env=hub,
    role=role_arn,
)

# Deploy the model to SageMaker Inference using a smaller `ml.g5.xlarge` instance
predictor = huggingface_model.deploy(
	initial_instance_count=1,
	instance_type="ml.g5.2xlarge",
	container_startup_health_check_timeout=300,
)

# Example usage: send a test request
response = predictor.predict({
    "inputs": "Hello, can you tell me more about LLaMA?",
})

print(f"Model response: {response}")
