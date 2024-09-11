import requests
import boto3
from requests_aws4auth import AWS4Auth
import json

# Initialize AWS credentials and session
session = boto3.Session()
credentials = session.get_credentials()
region = 'us-east-1'

# AWS4Auth will automatically retrieve AWS access and secret keys from your session
auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'sagemaker', session_token=credentials.token)

# Endpoint URL for your SageMaker model
url = 'https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/amastaytest/invocations'

# Headers for the POST request
headers = {
    'Content-Type': 'application/json'
}

def query_model(user_input):
    """
    Sends user input to the SageMaker endpoint and returns the model's response.
    """
    payload = {
        "inputs": user_input
    }
    
    # Send the POST request to SageMaker
    response = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload))
    
    # Decode the response
    response_body = response.json()
    
    return response_body.get('generated_text', 'No response received from the model.')

def chat_with_model():
    """
    Interactive chat loop where users can query the SageMaker model.
    """
    print("Welcome to the SageMaker AI chat. Type 'exit' to quit the chat.")
    
    while True:
        # Get user input
        user_input = input("You: ")

        # Exit the loop if the user types 'exit'
        if user_input.lower() == 'exit':
            print("Exiting chat. Goodbye!")
            break

        # Query the SageMaker model with the user's input
        ai_response = query_model(user_input)
        
        # Display the AI's response
        print(f"AI: {ai_response}")

# Start the interactive chat
if __name__ == "__main__":
    chat_with_model()
