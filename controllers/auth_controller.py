import logging
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)

# Route to send OTP to phone number
@auth_bp.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.json.get('phone_number')
    if not phone_number:
        logging.warning("Send OTP failed: Phone number is missing.")
        return jsonify({"error": "Phone number is required"}), 400
    
    result = AuthService.send_otp(phone_number)
    
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Send OTP error: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"Send OTP success: {result['message']}")
    return jsonify(result), 200

# Route to verify OTP and return session tokens
@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    phone_number = request.json.get('phone_number')
    otp = request.json.get('otp')

    if not phone_number or not otp:
        logging.warning("Verify OTP failed: Phone number or OTP is missing.")
        return jsonify({"error": "Phone number and OTP are required"}), 400
    
    result = AuthService.verify_otp(phone_number, otp)
    
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Verify OTP error: {result['error']}")
        return jsonify(result), 500
    
    logging.info("Verify OTP success.")
    return result  # Return Flask response with session tokens and headers

# Route to refresh tokens using the refresh token
@auth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    result = AuthService.refresh_token()
    
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Refresh Token error: {result['error']}")
        return jsonify(result), 500
    
    logging.info("Refresh Token success.")
    return result  # Return Flask response with new tokens in headers
