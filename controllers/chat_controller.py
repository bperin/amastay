from flask import jsonify
from chat_with_model import query_model

def handle_chat(request):
    """
    Handles the chat request and returns the AI response.
    """
    data = request.get_json()
    prompt = data.get('message', '')

    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    # Query the model with the user's input
    ai_response = query_model(prompt)

    return jsonify({"response": ai_response})
