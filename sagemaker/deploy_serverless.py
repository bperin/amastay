import json
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from sagemaker.serverless import ServerlessInferenceConfig  # Import the correct class
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Ensure the token is set properly
if hugging_face_hub_token is None:
    raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

# Hub Model configuration
hub = {"HF_MODEL_ID": "meta-llama/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8", "HF_TASK": "text-generation", "SM_NUM_GPUS": "1", "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token, "MESSAGES_API_ENABLED": "true", "QUANTIZE": "true"}

# Get the image URI for the model
image_uri = get_huggingface_llm_image_uri("huggingface")

# Use the correct SageMaker execution role ARN
role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

# Create Hugging Face Model Class
huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn)

# Create Serverless Inference Config Object (instead of dictionary)
serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=3072,  # We can potentially use less memory with quantized model
    max_concurrency=5,  # Maximum number of concurrent invocations
)

# Deploy the model using Serverless Inference
predictor = huggingface_model.deploy(serverless_inference_config=serverless_config)

# Save the deployed endpoint name for future use
endpoint_name = predictor.endpoint_name
print(f"Deployed endpoint (Serverless): {endpoint_name}")

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
