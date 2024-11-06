import json
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from sagemaker.serverless import ServerlessInferenceConfig
from dotenv import load_dotenv
import os


def deploy_llama_serverless(model_id="meta-llama/Llama-3.2-3B-Instruct-SpinQuant_INT4_EO8", memory_size_in_mb=4096, max_concurrency=2):  # Increased for 3B model  # Reduced concurrency due to model size
    # Load environment variables
    load_dotenv()
    hugging_face_hub_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

    if hugging_face_hub_token is None:
        raise ValueError("You must provide a valid Hugging Face Hub token in the .env file.")

    # Hub Model configuration for Llama 3.2 3B SpinQuant
    hub = {
        "HF_MODEL_ID": model_id,
        "HF_TASK": "text-generation",
        "HUGGING_FACE_HUB_TOKEN": hugging_face_hub_token,
        "MESSAGES_API_ENABLED": "true",
        # SpinQuant specific settings
        "USE_SPINQUANT": "true",
        "QUANTIZE": "true",
        "QUANTIZATION_APPROACH": "int4",
    }

    # Get the image URI for the model
    image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")  # Specify version that supports quantization

    # SageMaker role
    role_arn = "arn:aws:iam::422220778159:role/AmazonSageMaker-ExecutionRole"

    # Create Hugging Face Model Class
    huggingface_model = HuggingFaceModel(image_uri=image_uri, env=hub, role=role_arn)

    # Configure Serverless settings
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
    predictor = deploy_llama_serverless()

    # Test the endpoint
    test_input = {"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Explain what makes Llama 3.2 efficient for mobile devices?"}]}

    try:
        response = predictor.predict(test_input)
        print("\nModel Response:")
        print(response)
    except Exception as e:
        print(f"Inference failed: {str(e)}")

    # Uncomment to clean up
    # print("\nCleaning up endpoint...")
    # predictor.delete_endpoint()
