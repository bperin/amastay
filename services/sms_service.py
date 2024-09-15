from supabase_utils import supabase_client

def process_incoming_sms(phone_number: str, message: str) -> dict:
    """
    Process the incoming SMS message and prepare a response.
    Here you can integrate any business logic, including calling external services like SageMaker.
    """
    # Here you can handle logic such as calling SageMaker or other computations
    response_message = f"Processed your message: {message}"

    # Return the response as a dictionary
    return {
        'response_message': response_message
    }
