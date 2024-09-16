from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.json.get('phone_number')
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400
    
    result = AuthService.send_otp(phone_number)
    
    # Check if 'error' is in the result and handle accordingly
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result), 200

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    phone_number = request.json.get('phone_number')
    otp = request.json.get('otp')

    if not phone_number or not otp:
        return jsonify({"error": "Phone number and OTP are required"}), 400
    
    # Call the AuthService.verify_otp method and handle the response
    result = AuthService.verify_otp(phone_number, otp)
    
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result), 200

@auth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    result = AuthService.refresh_token()
    
    # Handle any errors from the AuthService
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result), 200
