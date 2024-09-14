from flask import jsonify
from services.otp_service import OtpService

class AuthController:
    
    @staticmethod
    def send_otp(request):
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        # Call the service to send OTP
        response = OtpService.send_otp(phone_number)
        if response.get('error'):
            return jsonify({"error": response['error']}), 500
        
        return jsonify({"message": "OTP sent successfully"}), 200

    @staticmethod
    def verify_otp(request):
        phone_number = request.json.get('phone_number')
        otp = request.json.get('otp')

        if not phone_number or not otp:
            return jsonify({"error": "Phone number and OTP are required"}), 400

        # Call the service to verify OTP
        response = OtpService.verify_otp(phone_number, otp)
        if response.get('error'):
            return jsonify({"error": response['error']}), 500
        
        return jsonify({"message": "OTP verified successfully"}), 200
