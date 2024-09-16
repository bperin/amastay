import json
import boto3
import os

# Initialize the SageMaker runtime client and SNS client
sagemaker_runtime = boto3.client('sagemaker-runtime')
sns_client = boto3.client('sns')


# Environment variables
ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME')  # SageMaker endpoint name
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')            # SNS topic ARN for sending SMS responses

def lambda_handler(event, context):
    """
    Handles incoming SMS, looks up booking and property info, queries the SageMaker AI model, and sends back a response.
    """
    # Extract message and phone number from SNS event
    sns_message = event['Records'][0]['Sns']['Message']
    phone_number = event['Records'][0]['Sns']['PhoneNumber']  # The sender's phone number
    
    # Step 1: Look up booking info based on the phone number
    booking_info = lookup_booking(phone_number)
    
    # Step 2: Look up property details
    property_info = get_property_details(booking_info['property_id'])
    
    # Step 3: Combine the SMS message, booking info, and property info to provide context
    context = {
        "message": sns_message,
        "booking_info": booking_info,
        "property_info": property_info
    }

    # Step 4: Send the context and message to the AI model
    ai_response = query_sagemaker_model(context)
    
    # Step 5: Send the AI-generated response back to the user via SMS
    send_sms_response(phone_number, ai_response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully.')
    }

def lookup_booking(phone_number):
    """
    Look up the booking details based on the user's phone number.
    Assumes the phone number is unique per booking.
    """
    # Query the Supabase bookings table for the booking associated with this phone number
    response = supabase.from_('bookings').select('*').eq('phone_number', phone_number).execute()
    
    if response.data:
        return response.data[0]  # Return the first booking record found
    else:
        raise Exception(f"No booking found for phone number {phone_number}")

def get_property_details(property_id):
    """
    Look up property details based on the property ID.
    """
    # Query the Supabase properties table for the property info associated with this booking
    response = supabase.from_('properties').select('*').eq('id', property_id).execute()
    
    if response.data:
        return response.data[0]  # Return the first property record found
    else:
        raise Exception(f"No property details found for property ID {property_id}")

def query_sagemaker_model(context):
    """
    Sends the user's message and context (booking and property details) to the SageMaker model and returns the AI's response.
    """
    # Send the context and message to the SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps({"inputs": context})
    )
    
    # Decode and parse the response
    response_body = response['Body'].read().decode('utf-8')
    result = json.loads(response_body)
    
    return result.get('generated_text', 'No response received from AI.')

def send_sms_response(phone_number, message):
    """
    Sends the AI-generated response back to the user via SNS SMS.
    """
    sns_client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
