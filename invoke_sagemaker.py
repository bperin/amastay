import boto3
import json

# Initialize the SageMaker runtime client
runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')

# Define the endpoint name (from your screenshot)
endpoint_name = 'amastay'

def invoke_model(prompt):
    # Define the payload, sending the prompt to the model
    payload = {
        "prompt": prompt
    }
    
    # Invoke the SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    # Read and parse the response
    result = json.loads(response['Body'].read().decode())
    
    return result

if __name__ == "__main__":
    prompt = "Hello model, how are you?"
    response = invoke_model(prompt)
    print(f"Model response: {response}")
