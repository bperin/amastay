# services/auth_service.py

from supabase_utils import supabase_client, supabase_admin_client
import logging
from flask import request
import requests
import time
from gotrue import UserResponse, AuthResponse


class AuthService:

    @staticmethod
    def sign_up_with_email_and_password(first_name: str, last_name: str, email: str, password: str, phone: str, user_type: str) -> AuthResponse:
        """
        Signs up a new user with user type metadata.

        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
            password: User's password
            phone: User's phone number
            user_type: User's type (e.g., owner)
        """
        try:
            user_metadata = {"first_name": first_name, "last_name": last_name, "phone": phone, "user_type": user_type}
            auth_response = supabase_client.auth.sign_up({"email": email, "options": {"data": user_metadata, "emailRedirectTo": "http://localhost:3000"}, "password": password})

            if not auth_response.user:
                error_message = auth_response.error.message if auth_response.error else "Failed to sign up user"
                logging.error(f"Failed to sign up user: {error_message}")
                raise Exception(error_message)

            logging.debug(f"User signed up with ID: {auth_response.user.id}")
            return auth_response

        except Exception as e:
            logging.error(f"Error during sign-up: {e}")
            raise

    @staticmethod
    def sign_in_with_email_and_password(email: str, password: str):
        """Logs in a user with email and password using direct Supabase REST API."""
        try:
            # Define the URL for Supabase's sign-in endpoint
            auth_url = f"{supabase_client.supabase_url}/auth/v1/token?grant_type=password"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key,
                "Authorization": f"Bearer {supabase_client.supabase_key}",
            }

            # Make the request to the Supabase auth endpoint
            response = requests.post(auth_url, json={"email": email, "password": password}, headers=headers)

            if response.status_code != 200:
                error_message = response.json().get("error_description", "Failed to sign in user")
                logging.error(f"Failed to sign in user: {error_message}")
                raise Exception(error_message)
            breakpoint()
            auth_response = response.json()
            logging.debug("User logged in successfully")
            return AuthService._build_session_response(auth_response)

        except Exception as e:
            logging.error(f"Error during login: {e}")
            raise

    @staticmethod
    def sign_in_with_google(credential: str, nonce: str = None):
        """Signs in or signs up a user with Google credentials using direct Supabase REST API."""
        try:
            # Define the URL for Supabase's OAuth sign-in endpoint
            auth_url = f"{supabase_client.supabase_url}/auth/v1/token?grant_type=id_token"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key,
                "Authorization": f"Bearer {supabase_client.supabase_key}",
            }

            # Prepare the request body
            body = {
                "id_token": credential,
                "provider": "google",
            }
            if nonce:
                body["nonce"] = nonce

            # Make the request to the Supabase auth endpoint
            response = requests.post(auth_url, json=body, headers=headers)

            if response.status_code == 200:
                auth_response = response.json()
                logging.debug("User signed in with Google successfully")
                return AuthService._build_session_response(auth_response)
            else:
                error_message = response.json().get("error_description", "Failed to authenticate with Google")
                logging.error(f"Failed to sign in with Google: {error_message}")
                raise Exception(error_message)

        except Exception as e:
            logging.error(f"Error during Google sign in: {e}")
            raise

    @staticmethod
    def refresh_token():
        """Refreshes the session tokens using the provided refresh token."""
        try:
            # Get refresh token from request body
            refresh_token = request.json.get("refresh_token")

            logging.debug(f"Received Refresh Token: {refresh_token}")

            if not refresh_token:
                logging.warning("No refresh token provided in the request")
                return {"error": "Refresh token is required"}, 400

            # Define the URL for Supabase's token refresh endpoint
            token_url = f"{supabase_client.supabase_url}/auth/v1/token?grant_type=refresh_token"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase_client.supabase_key,
                "Authorization": f"Bearer {supabase_client.supabase_key}",
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
                error_message = response.json().get("error_description", "Unknown error")
                logging.error(f"Failed to refresh session: {error_message}")
                raise Exception(error_message)

        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            raise

    @staticmethod
    def get_current_user() -> UserResponse | None:
        """Retrieves the current logged-in user's information."""
        try:
            # Get the access token from the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logging.warning("Authorization header missing or invalid")
                return {"error": "Authorization header missing or invalid"}, 401

            access_token = auth_header.split(" ")[1]

            user_response = supabase_client.auth.get_user(access_token)
            return user_response

        except Exception as e:
            logging.error(f"Error retrieving current user: {e}")
            raise

    @staticmethod
    def _build_session_response(auth_response):
        """Helper function to build the response with session tokens and user ID in headers."""
        user_id = auth_response["user"]["id"]

        # Determine expires_at
        expires_at = auth_response.get("expires_at")
        expires_in = auth_response.get("expires_in")

        # If expires_at is not provided, compute it from expires_in
        if not expires_at and expires_in:
            expires_at = int(time.time()) + int(expires_in)

        # Create a response with the tokens and user ID in the headers
        response = {"message": "Token issued successfully"}
        headers = {"x-access-token": auth_response["access_token"], "x-refresh-token": auth_response["refresh_token"], "x-expires-at": str(expires_at), "x-user-id": user_id}

        logging.debug(f"User ID {user_id} included in response headers")

        return response, 200, headers

    @staticmethod
    def request_password_reset(*, email: str):
        """
        Requests a password reset for the given email using Supabase REST API

        Args:
            email: User's email address
        """
        try:
            auth_url = f"{supabase_client.supabase_url}/auth/v1/recover"

            headers = {"Content-Type": "application/json", "apikey": supabase_client.supabase_key, "Authorization": f"Bearer {supabase_client.supabase_key}"}

            response = requests.post(auth_url, json={"email": email}, headers=headers)

            if response.status_code != 200:
                error_message = response.json().get("error_description", "Failed to request password reset")
                logging.error(f"Failed to request password reset: {error_message}")
                raise Exception(error_message)

            return {"message": "Password reset instructions sent to email"}, 200

        except Exception as e:
            logging.error(f"Error requesting password reset: {e}")
            raise

    @staticmethod
    def reset_password(*, access_token: str, new_password: str):
        """
        Resets the user's password using Supabase's verify_otp method

        Args:
            access_token: Recovery token from URL (the OTP)
            new_password: New password to set
        """
        try:
            # Verify the recovery token (OTP)
            verify_response = supabase_client.auth.verify_otp({"token_hash": access_token, "type": "recovery", "new_password": new_password})

            if not verify_response.user:
                logging.error("Failed to verify recovery token")
                raise Exception("Failed to reset password")

            return {"message": "Password reset successfully"}, 200

        except Exception as e:
            logging.error(f"Error resetting password: {e}")
            raise
