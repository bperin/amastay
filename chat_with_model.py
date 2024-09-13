import json
import boto3
from create_conversation import create_or_get_conversation
from get_renter_info import get_renter_info
from get_property_info import get_property_info
from get_message_history import get_message_history

# Initialize the SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Function to call the SageMaker model
def invoke_model(payload: str) -> str:
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='amastay',  # Replace with your actual endpoint name
            ContentType='application/json',
            Body=payload
        )
        response_body = response['Body'].read().decode('utf-8')
        model_response = json.loads(response_body)

        # Extract the generated text from the model's response
        generated_text = model_response.get('generated_text', "No response received.")
        return generated_text

    except Exception as e:
        return f"Error occurred while invoking the model: {str(e)}"

# Function to manage the SMS-based interaction with the AI model
def process_sms_message(booking_id: int, property_id: int, user_input: str):
    # Step 1: Create or fetch the conversation using booking_id and property_id
    conversation = create_or_get_conversation(booking_id, property_id)
    
    if not conversation:
        print("Failed to create or retrieve conversation.")
        return "Error: No conversation found."

    conversation_id = conversation['id']

    # Step 2: Fetch renter info and property info
    renter_info = get_renter_info(conversation['booking_id'])
    property_info = get_property_info(conversation['property_id'])

    # Step 3: Fetch recent message history
    message_history = get_message_history(conversation_id, limit=10)

    # Create the payload for the model
    context = {
        "roles": {
            "renter": renter_info,
            "ai": {"role": "AI Assistant"}
        },
        "property": property_info,
        "message_history": message_history,
        "user_input": user_input
    }
    input_payload = json.dumps(context)

    # Step 4: Invoke the model and get the response
    model_response = invoke_model(input_payload)

    # Step 5: Log the AI response in the conversation history (optional)
    # save_message_to_history(conversation_id, model_response, "AI")

    return model_response

# Example usage
if __name__ == "__main__":
    booking_id = 1
    property_id = 1
    user_input = "Can I bring my pet?"

    ai_response = process_sms_message(booking_id, property_id, user_input)
    print(f"AI Response: {ai_response}")
