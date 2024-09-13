import os
import boto3
from botocore.exceptions import NoCredentialsError

# Load credentials from environment variables
PINPOINT_ACCESS_KEY = os.getenv('PINPOINT_ACCESS_KEY')
PINPOINT_SECRET_ACCESS_KEY = os.getenv('PINPOINT_SECRET_ACCESS_KEY')
PINPOINT_REGION = os.getenv('PINPOINT_REGION', 'us-east-1')  # Default region if not set

# For testing, you can hardcode numbers like this:
# TEST_PHONE_NUMBERS = ['+1234567890', '+0987654321']

def get_client():
    try:
        client = boto3.client(
            'pinpoint',
            region_name=PINPOINT_REGION,
            aws_access_key_id=PINPOINT_ACCESS_KEY,
            aws_secret_access_key=PINPOINT_SECRET_ACCESS_KEY
        )
        return client
    except NoCredentialsError:
        print("Credentials not found.")
        return None

def send_sms(client, phone_number, message):
    try:
        response = client.send_messages(
            ApplicationId='your-application-id',  # Replace with your Pinpoint application ID
            MessageRequest={
                'Addresses': {
                    phone_number: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': 'TRANSACTIONAL'
                    }
                }
            }
        )
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

if __name__ == "__main__":
    client = get_client()
    if client:
        # Replace with actual phone numbers for testing
        phone_numbers = ['+14156025381']
        message = "Hello from Amazon Pinpoint!"
        for number in phone_numbers:
            response = send_sms(client, number, message)
            print(f"Sent message to {number}: {response}")
