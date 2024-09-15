import logging
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
    def refresh_token(refresh_token):
        try:
            logging.debug(f"Refreshing session with refresh token: {refresh_token}")
            
            # Call Supabase refresh session method
            refresh_response = supabase_client.auth.refresh_session({
                "refresh_token": refresh_token
            })

            if refresh_response:
                # After refreshing, call get_session to retrieve the new tokens
                session_response = supabase_client.auth.get_session()
                
                if session_response and session_response.access_token:
                    logging.debug(f"Session refreshed successfully")
                    return {
                        "access_token": session_response.access_token,
                        "refresh_token": session_response.refresh_token,
                        "expires_at": session_response.expires_at
                    }
                else:
                    return {"error": "Failed to retrieve session after refresh"}
            else:
                return {"error": "Failed to refresh session"}
        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return {"error": str(e)}
