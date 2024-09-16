from flask import Blueprint, request, jsonify
from services.ai_service import AIService
import logging

# Create a blueprint for the AI controller
ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat_with_model():
    """
    Endpoint to handle user conversations with the AI model.
    Expects the user_input in the request body. renter_id and conversation_id are optional.
    """
    data = request.get_json()

    renter_id = data.get('renter_id')
    conversation_id = data.get('conversation_id')
    user_input = data.get('user_input')

    if not user_input:
        return jsonify({"error": "user_input is required"}), 400

    # Log warnings if renter_id or conversation_id are missing
    if not renter_id:
        logging.warning("renter_id is missing in the request.")
    if not conversation_id:
        logging.warning("conversation_id is missing in the request.")

    try:
        # Call the AIService to handle the conversation
        ai_response = AIService.handle_conversation(renter_id, conversation_id, user_input)
        return jsonify({"response": ai_response}), 200
    except Exception as e:
        logging.error(f"Error during AIService.handle_conversation: {str(e)}")
        return jsonify({"error": "Failed to process the conversation"}), 500
