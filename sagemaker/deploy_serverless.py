import json
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig
from dotenv import load_dotenv
import os
import boto3


def deploy_quantized_model(model_id="TheBloke/TinyLlama-1.1B-Chat-v0.3-AWQ", memory_size_in_mb=4096, max_concurrency=2):
    # Load environment variables
    load_dotenv()
    hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

    if hugging_face_hub_token is None:
        raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

    # Configure model deployment parameters
    hub = {
        "HF_MODEL_ID": model_id,
        "HF_TASK": "text-generation",
        "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,
        "QUANTIZE": "true",
        "QUANTIZATION_APPROACH": "awq",
        "BITS": "4",  # Setting to use 4-bit quantization for reduced memory usage
    }

    # Image URI for us-east-1 region
    image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-torchserve:1.13.1-transformers4.28.0-gpu-py39-cu113-ubuntu20.04"

    # SageMaker execution role
    role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

    # Create Hugging Face Model instance with region specification
    huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn, region_name="us-east-1")  # Explicitly set region

    # Serverless Inference configuration
    serverless_config = ServerlessInferenceConfig(memory_size_in_mb=memory_size_in_mb, max_concurrency=max_concurrency)

    # Deploy the model
    try:
        predictor = huggingface_model.deploy(serverless_inference_config=serverless_config, wait=True)
        print(f"Deployed endpoint (Serverless): {predictor.endpoint_name}")
        return predictor
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Deploy the model
    predictor = deploy_quantized_model()

    # Test the endpoint with a sample input
    test_input = {"inputs": "Explain what makes Llama 3.2 efficient for mobile devices."}

    try:
        response = predictor.predict(test_input)
        print("\nModel Response:")
        print(response)
    except Exception as e:
        print(f"Inference failed: {str(e)}")

    # Uncomment to clean up
    # print("\nCleaning up endpoint...")
    # predictor.delete_endpoint()
