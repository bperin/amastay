from flask import Blueprint, request, jsonify
from services.sms_service import SMSService

# Create a Blueprint for SMS-related routes
sms_bp = Blueprint("sms_bp", __name__)


@sms_bp.route("/process_sms", methods=["POST"])
def handle_sms_request():
    """
    Handles the incoming SMS request and forwards it to the SMSService for processing.
    """
    data = request.get_json()
    phone_number = data.get("phone_number")
    message = data.get("message")

    if not phone_number or not message:
        return jsonify({"error": "Missing required fields"}), 400

    # Depending on the message, handle as a regular chat or lookup chat
    if "property" in message.lower():
        response_data = SMSService.handle_lookup_chat(phone_number, message)
    else:
        response_data = SMSService.handle_regular_chat(phone_number, message)

    return jsonify(response_data)
