# services/auth_service.py

from typing import Literal, Tuple
from supabase_utils import supabase_client, supabase_admin_client
import logging
from flask import Response, jsonify, make_response, request
import requests
import time
import secrets
import string
from gotrue import UserResponse, AuthResponse  # Add this at the top with other imports
from gotrue.types import Provider


class AuthService:

    @staticmethod
    def generate_random_password(length=12):
        """Generates a random string of letters, digits, and special characters."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def signup(first_name: str, last_name: str, email: str, password: str, phone: str, user_type: str):
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

            response = supabase_client.auth.sign_up({"email": email, "options": {"data": user_metadata, "emailRedirectTo": "http://localhost:3000"}, "password": password})

            if not response.user:
                error_message = response.error.message if response.error else "Failed to sign up user"
                logging.error(f"Failed to sign up user: {error_message}")
                return make_response(jsonify({"error": error_message}), 400)

            logging.debug(f"User signed up with ID: {response.user.id}")
            return make_response(jsonify({"message": "User created successfully"}), 200)

        except Exception as e:
            logging.error(f"Error during sign-up: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

    @staticmethod
    def login(email: str, password: str):
        """Logs in a user with email and password."""
        try:
            response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
            if response.session:
                breakpoint()
                return AuthService._build_session_response(response.session)
            else:
                error_message = response.error.message if response.error else "Failed to sign in user"
                logging.error(f"Failed to sign in user: {error_message}")
                return make_response(jsonify({"error": error_message}), 400)
        except Exception as e:
            logging.error(f"Error during login: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

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
                return {"error": error_message}, 500

        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def get_current_user() -> UserResponse | None:
        """Retrieves the current logged-in user's information."""
        try:
            # Get the access token from the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logging.warning("Authorization header missing or invalid")
                return (
                    jsonify({"error": "Authorization header missing or invalid"}),
                    401,
                )

            access_token = auth_header.split(" ")[1]

            user_response = supabase_client.auth.get_user(access_token)
            return user_response

        except Exception as e:
            logging.error(f"Error retrieving current user: {e}")
            return jsonify({"error": str(e)}), 500

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
        res = make_response(jsonify({"message": "Token issued successfully"}), 200)
        res.headers["x-access-token"] = auth_response["access_token"]
        res.headers["x-refresh-token"] = auth_response["refresh_token"]
        res.headers["x-expires-at"] = str(expires_at)
        res.headers["x-user-id"] = user_id  # Add the user ID to the headers

        logging.debug(f"User ID {user_id} included in response headers")

        return res

    @staticmethod
    def logout():
        return supabase_client.auth.sign_out()

    @staticmethod
    def sign_in_with_google(credential: str, nonce: str = None):
        """Signs in or signs up a user with Google credentials."""
        try:
            # Sign in with Google ID token
            response = supabase_client.auth.sign_in_with_id_token({"provider": Provider.google, "token": credential, "nonce": nonce})

            if response.session:
                # Build response similar to OTP verification
                auth_response = {"access_token": response.session.access_token, "refresh_token": response.session.refresh_token, "expires_in": response.session.expires_in, "user": {"id": response.session.user.id}}
                return AuthService._build_session_response(auth_response)
            else:
                error_message = "Failed to authenticate with Google"
                logging.error(error_message)
                return make_response(jsonify({"error": error_message}), 400)

        except Exception as e:
            logging.error(f"Error during Google sign in: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

    @staticmethod
    def create_manager_invitation(owner_id: str, email: str, team_id: str) -> Tuple[Response, int]:
        """
        Creates an invitation for a manager to join a team.

        Args:
            owner_id: ID of the owner creating the invitation
            email: Email address of the invited manager
            team_id: ID of the team the manager is being invited to
        """
        try:
            # Generate a temporary password for the manager
            temp_password = AuthService.generate_random_password()

            # Create the user account with manager role
            user_metadata = {"role": "manager", "owner_id": owner_id, "team_id": team_id, "invitation_pending": True}

            response = supabase_admin_client.auth.admin.create_user({"email": email, "password": temp_password, "email_confirm": True, "user_metadata": user_metadata})

            if not response.user:
                return jsonify({"error": "Failed to create manager account"}), 400

            # Here you would typically send an email to the manager with their credentials
            # and a link to set up their account

            return jsonify({"message": "Manager invitation created successfully", "user_id": response.user.id}), 200

        except Exception as e:
            logging.error(f"Error creating manager invitation: {e}")
            return jsonify({"error": str(e)}), 500
