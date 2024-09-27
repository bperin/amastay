import logging
import requests
from flask import make_response, jsonify, request
from supabase_utils import supabase_client,supabase_admin_client

class AuthService:

    @staticmethod
    def send_otp(phone_number):
        """Sends OTP to the specified phone number using Supabase's OTP functionality via API."""
        try:
            # Define the URL for Supabase's OTP sending endpoint
            otp_url = f"{supabase_client.supabase_url}/auth/v1/otp"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key
            }

            # Make the request to send OTP
            response = requests.post(otp_url, json={"phone": phone_number}, headers=headers)

            logging.debug(f"Supabase OTP Response Status: {response.status_code}")
            logging.debug(f"Supabase OTP Response Body: {response.text}")

            if response.status_code == 200:
                logging.debug(f"OTP sent successfully to {phone_number}")
                return {"message": "OTP sent"}
            else:
                error_message = response.json().get('error_description', 'Failed to send OTP')
                logging.error(f"Failed to send OTP: {error_message}")
                return {"error": error_message}

        except Exception as e:
            logging.error(f"Error sending OTP: {e}")
            return {"error": str(e)}

    @staticmethod
    def verify_otp(phone_number, otp):
        """Verifies the OTP for the given phone number using Supabase's API."""
        try:
            logging.debug(f"Verifying OTP for phone number: {phone_number}, OTP: {otp}")
            
            # Define the URL for Supabase's OTP verification endpoint
            verify_url = f"{supabase_client.supabase_url}/auth/v1/verify"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key
            }

            # Make the request to verify the OTP
            response = requests.post(verify_url, json={"phone": phone_number, "token": otp, "type": "sms"}, headers=headers)

            logging.debug(f"Supabase OTP Verification Response Status: {response.status_code}")
            logging.debug(f"Supabase OTP Verification Response Body: {response.text}")

            if response.status_code == 200:
                auth_response = response.json()
                logging.debug(f"OTP verified successfully for {phone_number}")
                return AuthService._build_session_response(auth_response)
            else:
                error_message = response.json().get('error_description', 'OTP verification failed')
                logging.error(f"Failed to verify OTP: {error_message}")
                return {"error": error_message}

        except Exception as e:
            logging.error(f"Error verifying OTP: {e}")
            return {"error": str(e)}

    @staticmethod
    def refresh_token():
        """Refreshes the session token using the provided refresh token from the POST parameter."""
        try:
            # Get refresh token from request body
            refresh_token = request.json.get('refresh_token')

            logging.debug(f"Received Refresh Token: {refresh_token}")

            if not refresh_token:
                logging.warning("No refresh token provided in the request")
                return jsonify({"error": "Refresh token is required"}), 400

            # Define the URL for Supabase's token refresh endpoint
            token_url = f"{supabase_client.supabase_url}/auth/v1/token?grant_type=refresh_token"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key,
                "Authorization": f"Bearer {refresh_token}"
            }

            # Make the request to the Supabase token endpoint
            response = requests.post(token_url, json={"refresh_token": refresh_token}, headers=headers)

            logging.debug(f"Supabase Response Status: {response.status_code}")
            logging.debug(f"Supabase Response Body: {response.text}")

            if response.status_code == 200:
                auth_response = response.json()
                logging.debug("Session refreshed successfully")
                return AuthService._build_session_response(auth_response)
            else:
                error_message = response.json().get('error_description', 'Unknown error')
                logging.error(f"Failed to refresh session: {error_message}")
                return jsonify({"error": error_message}), 500

        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def _build_session_response(auth_response):
        print(auth_response)
        """Helper function to build the response with session tokens and user ID in headers."""
        user_id = auth_response['user']['id']
        
        # Create a response with the tokens and user ID in the headers
        res = make_response(jsonify({"message": "Token issued successfully"}), 200)
        res.headers['x-access-token'] = auth_response['access_token']
        res.headers['x-refresh-token'] = auth_response['refresh_token']
        res.headers['x-expires-at'] = auth_response['expires_at']
        res.headers['x-user-id'] = user_id  # Add the user ID to the headers

        logging.debug(f"User ID {user_id} included in response headers")

        return res
    
    @staticmethod
    def get_user_by_id(user_id):
        print("get user by id")
        print(user_id)
        """Retrieve user information from Supabase by user ID."""
        print(user_id)
        try:
            # Use Supabase's auth API to get the user
            response = supabase_admin_client.auth.admin.get_user_by_id(user_id)
            if response.error:
                logging.error(f"Error fetching user: {response.error.message}")
                return None

            print("GOT USER")
            print(response)
            user = response.user

            # Construct user info to return
            user_info = {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'app_metadata': user.app_metadata,
                'user_metadata': user.user_metadata,
                'created_at': user.created_at,
                'confirmed_at': user.confirmed_at,
                'last_sign_in_at': user.last_sign_in_at,
                'role': user.role,
                # Add other fields as needed
            }

            return user_info

        except Exception as e:
            logging.error(f"Error retrieving user by ID: {e}")
            return None
