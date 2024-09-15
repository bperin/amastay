from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    phone_number = request.json.get('phone_number')
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400
    
    result = AuthService.send_otp(phone_number)
    return jsonify(result), 200 if 'message' in result else 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    phone_number = request.json.get('phone_number')
    otp = request.json.get('otp')
    
    if not phone_number or not otp:
        return jsonify({"error": "Phone number and OTP are required"}), 400
    
    result = AuthService.verify_otp(phone_number, otp)
    return jsonify(result), 200 if 'access_token' in result else 401

@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    return AuthService.refresh_token()
