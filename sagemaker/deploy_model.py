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
model_id = "meta-llama/Llama-3.2-3B-Instruct"
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

# Check if model and endpoint already exist
model_exists = False
endpoint_exists = False

# Initialize the SageMaker client
sagemaker_client = boto3.client("sagemaker")

try:
    sagemaker_client.describe_model(ModelName=model_name)
    model_exists = True
    print(f"Model {model_name} already exists")
except sagemaker_client.exceptions.ClientError:
    model_exists = False

try:
    sagemaker_client.describe_endpoint(EndpointName=model_name)
    endpoint_exists = True
    print(f"Endpoint {model_name} already exists")
except sagemaker_client.exceptions.ClientError:
    endpoint_exists = False

if not model_exists:
    # Create the model
    huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn, name=model_name)
    print(f"Created model: {model_name}")

if not endpoint_exists:
    # Deploy the model to a provisioned endpoint
    predictor = huggingface_model.deploy(initial_instance_count=1, instance_type="ml.g5.2xlarge", endpoint_name=model_name, container_startup_health_check_timeout=300)
    print(f"Deployed endpoint: {model_name}")

    # Send test request to the deployed model endpoint
    response = predictor.predict(
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that can understand images and text."},
                {"role": "user", "content": "What is deep learning?"},
            ]
        }
    )

    print(response)

    # Clean up the endpoint when not needed (uncomment this line to delete the endpoint)
    # predictor.delete_endpoint()
else:
    print(f"Skipping deployment as endpoint {model_name} already exists")
