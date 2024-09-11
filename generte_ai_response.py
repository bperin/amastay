import json
from typing import List, Dict
from get_message_history import get_message_history

def generate_ai_response(conversation_id: int, user_input: str, limit: int = 10) -> str:
    """Generates an AI response using recent message history as context.
    
    Args:
        conversation_id (int): The ID of the conversation.
        user_input (str): The latest input from the renter.
        limit (int): The maximum number of recent messages to retrieve.

    Returns:
        str: The AI-generated response.
    """
    # Fetch recent message history
    message_history = get_message_history(conversation_id, limit)
    
    # Prepare context to send to the AI
    context = {
        "recent_messages": message_history,
        "user_input": user_input
    }

    # Call the AI service (example function - replace with actual AI API call)
    ai_response = call_ai_model(json.dumps(context))

    return ai_response

def call_ai_model(context: str) -> str:
    """Simulated function to call the AI model. Replace with actual API call."""
    # Simulate AI processing
    return f"AI response based on context: {context}"

# Example usage
if __name__ == "__main__":
    conversation_id = 1
    user_input = "What time is check-in?"
    ai_response = generate_ai_response(conversation_id, user_input)
    print(f"AI Response: {ai_response}")
