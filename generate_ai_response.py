import json
import boto3
from get_message_history import get_message_history

# Set up the SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

def generate_ai_response(conversation_id: int, user_input: str, limit: int = 10) -> str:
    """Generates an AI response using recent message history as context."""
    
    # Step 1: Fetch recent message history
    message_history = get_message_history(conversation_id, limit)
    
    # Step 2: Fetch renter and property info (hard-coded for now)
    renter_info = {
        "name": "John Doe",
        "role": "Renter"
    }
    
    property_info = {
        "name": "Beautiful Beach House",
        "address": "123 Ocean Ave, Santa Monica, CA",
        "description": "A lovely beachfront property with amazing views.",
        "document": "General property info document (amenities, policies, etc.)"
    }
    
    # Step 3: Prepare context to send to the AI
    context = {
        "roles": {
            "renter": renter_info,
            "ai": {"role": "AI Assistant"}
        },
        "property": property_info,
        "message_history": message_history,
        "user_input": user_input
    }
    
    # Step 4: Convert context to JSON string
    input_payload = json.dumps(context)
    
    # Step 5: Call the SageMaker AI endpoint with the input context
    ai_response = invoke_model(input_payload)

    return ai_response

def invoke_model(payload: str) -> str:
    """Calls the SageMaker AI model and returns the response."""
    
    try:
        # Make the request to SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='amastay',  # Replace with your actual endpoint name
            ContentType='application/json',
            Body=payload
        )
        
        # Decode the response
        response_body = response['Body'].read().decode('utf-8')
        model_response = json.loads(response_body)
        
        # Extract the generated response text
        generated_text = model_response.get('generated_text', "No response")
        
        return generated_text
    
    except Exception as e:
        print(f"Error invoking model: {e}")
        return "There was an error processing your request."

# Example usage
if __name__ == "__main__":
    conversation_id = 1
    user_input = "Can I bring my pet with me?"
    
    # Generate the AI response
    ai_response = generate_ai_response(conversation_id, user_input)
    print(f"AI Response: {ai_response}")
