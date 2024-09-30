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
    "SM_NUM_GPUS": "1",
    "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,
    "MESSAGES_API_ENABLED": "true",
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

# Deploy the model to SageMaker Inference
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",
    container_startup_health_check_timeout=300,
)

# Save the deployed endpoint name for future use
endpoint_name = predictor.endpoint_name
print(f"Deployed endpoint: {endpoint_name}")

# Send request
response = predictor.predict(
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is deep learning?"},
        ]
    }
)

print(response)


# Clean up the endpoint when not needed
# predictor.delete_endpoint()
