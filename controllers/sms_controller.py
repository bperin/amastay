from flask import request, jsonify
from services.sms_service import process_incoming_sms

def handle_sms_request():
    """
    Handles the incoming SMS request and forwards it to the service for processing.
    """
    data = request.json
    phone_number = data.get('phone_number')
    message = data.get('message')
    
    if not phone_number or not message:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Call the service to process the SMS
    response_data = process_incoming_sms(phone_number, message)

    return jsonify(response_data)
