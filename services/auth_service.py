import logging
from flask import make_response, jsonify
from supabase_utils import supabase_client

class AuthService:
    
    @staticmethod
    def send_otp(phone_number):
        """Sends OTP to the specified phone number using Supabase's OTP functionality."""
        try:
            response = supabase_client.auth.sign_in_with_otp({"phone": phone_number})
            if response:
                logging.debug(f"OTP sent successfully to {phone_number}")
                return {"message": "OTP sent"}
            else:
                return {"error": "Failed to send OTP"}
        except Exception as e:
            logging.error(f"Error sending OTP: {e}")
            return {"error": str(e)}

    @staticmethod
    def verify_otp(phone_number, otp):
        """Verifies the OTP for the given phone number using Supabase."""
        try:
            logging.debug(f"Verifying OTP for phone number: {phone_number}, OTP: {otp}")
            
            # Verify OTP using Supabase's OTP verification method
            response = supabase_client.auth.verify_otp({
                "phone": phone_number, 
                "token": otp, 
                "type": "sms"
            })
            
            if response and response.session:
                logging.debug(f"OTP verified successfully for {phone_number}")

                # Call helper to return session tokens and headers
                return AuthService._build_session_response(response)
            else:
                logging.error(f"OTP verification failed for {phone_number}")
                return {"error": "OTP verification failed"}
        
        except Exception as e:
            logging.error(f"Error verifying OTP: {e}")
            return {"error": str(e)}

    @staticmethod
    def refresh_token():
        """Refreshes the session token using the provided refresh token from the request headers."""
        refresh_token = request.headers.get('x-refresh-token')

        logging.debug(f"Received Refresh Token: {refresh_token}")

        if not refresh_token:
            logging.warning("No refresh token provided in the request headers")
            return jsonify({"error": "Refresh token is required"}), 400

        try:
            # Refresh the session using Supabase
            response = supabase_client.auth.refresh_session({"refresh_token": refresh_token})

            if response and response.session.access_token:
                logging.debug("Session refreshed successfully")

                # Call helper to return session tokens and headers
                return AuthService._build_session_response(response)
            else:
                logging.error("Failed to refresh session")
                return jsonify({"error": "Failed to refresh session"}), 500

        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def _build_session_response(auth_response):
        """Helper function to build the response with session tokens and user ID in headers."""
        
        user_id = auth_response.user.id  # Get the user ID from the session response
        
        # Create a response with the tokens and user ID in the headers
        res = make_response(jsonify({"message": "Token issued successfully"}), 200)
        res.headers['x-access-token'] = auth_response.session.access_token
        res.headers['x-refresh-token'] = auth_response.session.refresh_token
        res.headers['x-expires-at'] = auth_response.session.expires_at
        res.headers['x-user-id'] = user_id  # Add the user ID to the headers

        logging.debug(f"User ID {user_id} included in response headers")

        return res
