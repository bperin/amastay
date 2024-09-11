import json
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Load AWS credentials from environment variables
access_key = os.getenv('SAGEMAKER_ACCESS_KEY')
secret_access_key = os.getenv('SAGEMAKER_SECRET_ACCESS_KEY')

# Load the SageMaker endpoint name and region
ENDPOINT_NAME = "amastay"  # Replace with your endpoint name if different
REGION = "us-east-1"  # Replace with your region if necessary

def query_sagemaker(prompt):
    """
    Query the SageMaker endpoint with a text prompt.
    """
    try:
        # Initialize the SageMaker runtime client with credentials
        sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            region_name=REGION,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key
        )

        # Prepare the payload for the model
        payload = {
            'inputs': prompt
        }

        # Call the SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(payload)  # Convert the payload to a JSON string
        )

        # Decode the response
        result = json.loads(response['Body'].read().decode('utf-8'))
        return result

    except NoCredentialsError as e:
        return f"No credentials found: {str(e)}"
    except PartialCredentialsError as e:
        return f"Partial credentials error: {str(e)}"
    except Exception as e:
        return f"Error querying SageMaker endpoint: {str(e)}"

if __name__ == "__main__":
    # Ask the user for input
    prompt = input("Please enter your prompt: ")

    # Call the SageMaker endpoint
    result = query_sagemaker(prompt)
    
    # Print the result from the model
    print("Model Response:", result)
