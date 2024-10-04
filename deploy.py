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
huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn)

# Update instance type based on GPU requirements
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",
    container_startup_health_check_timeout=300,
    max_runtime_in_seconds=300,  # Changed to 5 minutes (300 seconds) of inactivity before shutdown
)

# Save the deployed endpoint name for future use
endpoint_name = predictor.endpoint_name
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

# Clean up the endpoint when not needed (uncomment this line to delete the endpoint)
# predictor.delete_endpoint()
