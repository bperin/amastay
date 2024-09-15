# Ensure this is the correct path where your AuthService file exists
from services.auth_service import AuthService
from flask import request, jsonify, make_response
import logging

class AuthController:

    @staticmethod
    def send_otp(request):
        phone_number = request.json.get('phone_number')

        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        # Call the AuthService to send OTP
        response = AuthService.send_otp(phone_number)
        if response.get('error'):
            return jsonify({"error": response['error']}), 500
        
        return jsonify({"message": response['message']}), 200

    @staticmethod
    def verify_otp(request):
        phone_number = request.json.get('phone_number')
        otp = request.json.get('otp')

        if not phone_number or not otp:
            return jsonify({"error": "Phone number and OTP are required"}), 400

        # Call the AuthService to verify OTP and get session data (access and refresh tokens)
        session_response = AuthService.verify_otp(phone_number, otp)
        if session_response.get('error'):
            return jsonify({"error": session_response['error']}), 500

        # Set session tokens in headers
        res = make_response(jsonify({"message": "OTP verified successfully"}), 200)
        res.headers['X-Access-Token'] = session_response['access_token']
        res.headers['X-Refresh-Token'] = session_response['refresh_token']
        res.headers['X-Expires-At'] = session_response['expires_at']
        return res

    @staticmethod
    def refresh_token(request):
        refresh_token = request.headers.get('X-Refresh-Token')
        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400

        # Call the AuthService to refresh the token
        session_response = AuthService.refresh_token(refresh_token)
        if 'error' in session_response:
            return jsonify(session_response), 500

        # Set refreshed tokens in the headers
        res = make_response(jsonify({"message": "Token refreshed successfully"}), 200)
        res.headers['X-Access-Token'] = session_response['access_token']
        res.headers['X-Refresh-Token'] = session_response['refresh_token']
        res.headers['X-Expires-At'] = session_response['expires_at']
        return res
