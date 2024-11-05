import json
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from dotenv import load_dotenv
import os
import boto3

# Load environment variables from .env file
load_dotenv()

# Hugging Face Hub token from .env
hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Ensure the token is set properly
if hugging_face_hub_token is None:
    raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

# Hub Model configuration
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
hub = {
    "HF_MODEL_ID": model_id,
    "HF_TASK": "text-generation",
    "SM_NUM_GPUS": "1",  # Number of GPUs to use
    "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,
    "MESSAGES_API_ENABLED": "true",
}

# Get the image URI for the model
image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

# Use the correct SageMaker execution role ARN
role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

# Create a valid model name (alphanumeric and hyphens only, must start and end with alphanumeric)
model_name = model_id.replace("/", "-").replace(".", "-").lower()
if model_name.startswith("-"):
    model_name = "model" + model_name
if model_name.endswith("-"):
    model_name = model_name + "1"

# Initialize the SageMaker client
sagemaker_client = boto3.client("sagemaker")

try:
    # Check if endpoint config exists and delete it if it does
    try:
        sagemaker_client.delete_endpoint_config(EndpointConfigName=model_name)
        print(f"Deleted existing endpoint config: {model_name}")
    except sagemaker_client.exceptions.ClientError:
        pass  # Endpoint config doesn't exist, which is fine

    # Check if endpoint exists and delete it if it does
    try:
        sagemaker_client.delete_endpoint(EndpointName=model_name)
        print(f"Deleted existing endpoint: {model_name}")
        # Wait for the endpoint to be deleted
        waiter = sagemaker_client.get_waiter("endpoint_deleted")
        waiter.wait(EndpointName=model_name)
    except sagemaker_client.exceptions.ClientError:
        pass  # Endpoint doesn't exist, which is fine

    # Create HuggingFace model instance
    huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn, transformers_version="4.28", pytorch_version="2.0", py_version="py310", model_server_workers=1, name=model_name)

    print(f"Created model: {model_name}")

    # Deploy the model to an endpoint
    predictor = huggingface_model.deploy(initial_instance_count=1, instance_type="ml.g5.2xlarge", endpoint_name=model_name)

    print(f"Model deployed to endpoint: {predictor.endpoint_name}")

    # Test the endpoint with a sample request
    sample_payload = {"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is machine learning?"}]}

    response = predictor.predict(sample_payload)
    print(f"Test response: {response}")

except Exception as e:
    print(f"Error deploying model: {str(e)}")
