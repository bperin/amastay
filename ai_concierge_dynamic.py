import os
import json
import boto3
from supabase_utils import supabase_client


# Load AWS credentials for SageMaker and Supabase client from environment variables
SAGEMAKER_ACCESS_KEY = os.getenv('SAGEMAKER_ACCESS_KEY')
SAGEMAKER_SECRET_ACCESS_KEY = os.getenv('SAGEMAKER_SECRET_ACCESS_KEY')
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT')


# SageMaker runtime client
sagemaker_runtime = boto3.client(
    'sagemaker-runtime',
    aws_access_key_id=SAGEMAKER_ACCESS_KEY,
    aws_secret_access_key=SAGEMAKER_SECRET_ACCESS_KEY
)

# Base role definition
BASE_ROLE_DESCRIPTION = """
You are a rental concierge assistant. Your role is to help renters by providing property details, answering questions about amenities, offering local recommendations, and handling basic customer service requests.
You should use the available booking and property information to provide relevant and personalized responses.
"""

def get_booking_context(renter_id):
    """
    Fetch booking context for the given renter.
    """
    response = supabase_client.from_('bookings').select('*').eq('renter_id', renter_id).execute()
    
    if response.data:
        booking = response.data[0]
        property_response = supabase_client.from_('properties').select('*').eq('property_id', booking['property_id']).execute()
        
        if property_response.data:
            property_data = property_response.data[0]
            return booking, property_data
    
    return None, None

def query_sagemaker_with_context(prompt, booking_context, property_context):
    """
    Send a prompt to SageMaker along with booking and property context.
    """
    # Add context to the prompt
    context_prompt = f"{BASE_ROLE_DESCRIPTION}\n\nBooking Info:\n{booking_context}\n\nProperty Info:\n{property_context}\n\nUser Prompt: {prompt}"

    # Call SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps({"inputs": context_prompt})
    )
    
    # Decode the response
    result = json.loads(response['Body'].read().decode('utf-8'))
    return result

def handle_conversation(renter_id, prompt):
    """
    Main function to handle the conversation with the renter by pulling relevant booking and property data.
    """
    # Fetch booking and property context
    booking_context, property_context = get_booking_context(renter_id)

    if not booking_context or not property_context:
        return "Sorry, I couldn't find your booking information. Please check back later or contact support."

    # Query SageMaker with the dynamic context
    response = query_sagemaker_with_context(prompt, booking_context, property_context)

    return response


# Example Usage
if __name__ == "__main__":
    # Mock renter_id and user prompt
    renter_id = "renter-uuid-5678"  # Replace with actual renter UUID
    user_prompt = input("Ask the Rental Concierge Assistant: ")

    # Get the AI's response
    ai_response = handle_conversation(renter_id, user_prompt)
    print("AI Response:", ai_response)
