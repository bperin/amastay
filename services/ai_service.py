import json
import os
import boto3
import logging
from supabase_utils import supabase_client

# Load environment variables
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_service.log"),
        logging.StreamHandler()
    ]
)

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

BASE_ROLE_DESCRIPTION = """
You are a rental concierge assistant. Your role is to help renters by providing property details, answering questions about amenities, offering local recommendations, and handling basic customer service requests.
You should use the available booking and property information to provide relevant and personalized responses.
"""

class AIService:

    @staticmethod
    def query_model(user_input: str, context: str) -> str:
        """
        Sends the user's input and context to the SageMaker model and returns the model's response.
        """
        payload = {"inputs": f"{context}\nUser Input: {user_input}"}
        try:
            # Invoke the SageMaker model endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            response_body = response['Body'].read().decode('utf-8')
            model_response = json.loads(response_body)
            logging.info(f"Model response: {model_response}")

            # Handle the model response (list or dict format)
            if isinstance(model_response, list):
                return model_response[0].get('generated_text', 'No response received.')
            elif isinstance(model_response, dict):
                return model_response.get('generated_text', 'No response received.')
            else:
                return "Unexpected response format received."

        except Exception as e:
            logging.error(f"Error invoking SageMaker model: {e}")
            return "Error occurred while invoking the model."

    @staticmethod
    def get_booking_context(renter_id):
        """
        Fetches booking context for the given renter.
        """
        if not renter_id:
            logging.warning("No renter_id provided.")
            return None, None

        booking_response = supabase_client.from_('bookings').select('*').eq('renter_id', renter_id).execute()
        if booking_response.data:
            booking = booking_response.data[0]
            property_response = supabase_client.from_('properties').select('*').eq('id', booking['property_id']).execute()
            if property_response.data:
                property_data = property_response.data[0]
                return booking, property_data
        return None, None

    @staticmethod
    def get_message_history(conversation_id: int, limit: int = 10):
        """
        Fetches the recent message history for a conversation.
        """
        if not conversation_id:
            logging.warning("No conversation_id provided.")
            return []

        response = supabase_client.from_('messages').select('*').eq('conversation_id', conversation_id).order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []

    @staticmethod
    def handle_conversation(renter_id=None, conversation_id=None, user_input=None):
        """
        Handles the conversation with the renter by pulling relevant message history, booking, and property data.
        """
        if not user_input:
            logging.error("No user_input provided.")
            return "Error: No user input provided."

        # Step 1: Fetch message history (optional)
        message_history = AIService.get_message_history(conversation_id)

        # Step 2: Fetch booking and property context (optional)
        booking_context, property_context = AIService.get_booking_context(renter_id)

        # Step 3: Construct context from available data
        context = BASE_ROLE_DESCRIPTION

        if booking_context and property_context:
            context += f"\n\nBooking Info:\n{booking_context}\nProperty Info:\n{property_context}\n"

        if message_history:
            context += f"\n\nMessage History:\n{message_history}"

        # Step 4: Query the model with the constructed context and user input
        ai_response = AIService.query_model(user_input, context)

        return ai_response
