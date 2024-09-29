from flask import Blueprint, request, jsonify
from services.ai_service import AIService

# Create a blueprint for the AI controller
ai_bp = Blueprint("ai_bp", __name__)


@ai_bp.route("/chat", methods=["POST"])
def chat_with_model():
    """
    Basic chat endpoint that interacts with the AI model.
    Expects 'user_input' in the request body. Does not require additional context.
    """
    data = request.get_json()
    user_input = data.get("user_input")

    if not user_input:
        return jsonify({"error": "user_input is required"}), 400

    # Call the AIService to handle the conversation
    ai_response = AIService.query_model(user_input)

    return jsonify({"response": ai_response}), 200
