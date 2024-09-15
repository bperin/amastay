import logging
from flask import jsonify, make_response, request
from supabase_utils import supabase_client

class AuthService:

    @staticmethod
    def send_otp(phone_number):
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
        try:
            logging.debug(f"Verifying OTP for phone number: {phone_number}, OTP: {otp}")
            
            # Verify OTP
            response = supabase_client.auth.verify_otp({
                "phone": phone_number, 
                "token": otp, 
                "type": "sms"
            })
            
            if response and response.user:
                logging.debug(f"OTP verified successfully for {phone_number}")
                
                # Retrieve the session with tokens after OTP verification
                session_response = supabase_client.auth.get_session()

                if session_response and session_response.access_token:
                    return {
                        "access_token": session_response.access_token,
                        "refresh_token": session_response.refresh_token,
                        "expires_at": session_response.expires_at
                    }
                return {"error": "Failed to retrieve session information"}
            return {"error": "OTP verification failed"}
        except Exception as e:
            logging.error(f"Error verifying OTP: {e}")
            return {"error": str(e)}

    @staticmethod
    def refresh_token():
        """
        Extract the refresh token from the request headers and call Supabase to refresh the session.
        """
        # Retrieve the refresh token from the headers
        refresh_token = request.headers.get('X-Refresh-Token')

        # Log the received refresh token
        logging.debug(f"Received Refresh Token: {refresh_token}")

        # If no refresh token is provided, return an error
        if not refresh_token:
            logging.warning("No refresh token provided in the request headers")
            return jsonify({"error": "Refresh token is required"}), 400

        try:
            # Call Supabase to refresh the session using the provided refresh token
            response = supabase_client.auth.refresh_session({"refresh_token": refresh_token})

            if response and response.access_token:
                logging.debug("Session refreshed successfully")
                # Set the new tokens in the response headers
                res = make_response(jsonify({"message": "Token refreshed successfully"}), 200)
                res.headers['X-Access-Token'] = response.access_token
                res.headers['X-Refresh-Token'] = response.refresh_token
                res.headers['X-Expires-At'] = response.expires_at

                return res
            else:
                logging.error("Failed to refresh session")
                return jsonify({"error": "Failed to refresh session"}), 500

        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return jsonify({"error": str(e)}), 500
