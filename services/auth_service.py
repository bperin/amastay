# services/auth_service.py

from supabase_utils import supabase, auth, supabase_admin
from fastapi import HTTPException
from typing import Optional
import logging
import requests
import time
from gotrue import UserResponse, Session, AuthResponse
from phone_utils import PhoneUtils

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def sign_up_with_email_and_password(email: str, password: str, phone: str, first_name: str, last_name: str, user_type: str = "owner"):
        try:
            # Create user with the new auth client
            auth_response = auth.sign_up({"email": email, "password": password, "phone": phone, "data": {"first_name": first_name, "last_name": last_name, "user_type": user_type}})

            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Failed to create user")

            return auth_response

        except Exception as e:
            logger.error(f"Sign up failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def sign_in_with_email_and_password(email: str, password: str):
        logger.info(f"Attempting sign in for email: {email[:3]}***")
        try:
            # Basic auth - no extra options needed
            logger.debug("Calling Supabase auth.sign_in_with_password")
            auth_response = auth.sign_in_with_password({"email": email, "password": password})

            logger.debug(f"Raw auth response type: {type(auth_response)}")
            logger.debug(f"Raw auth response: {auth_response}")

            if not auth_response:
                logger.error("No auth response received from Supabase")
                raise HTTPException(status_code=401, detail="Authentication failed")

            logger.debug(f"Auth response has session: {hasattr(auth_response, 'session')}")
            if not auth_response.session:
                logger.error("Auth response missing session data")
                raise HTTPException(status_code=401, detail="No session created")

            logger.info(f"Authentication successful for {email[:3]}***")
            logger.debug(f"Session expires at: {auth_response.session.expires_at}")
            return auth_response.session

        except HTTPException as he:
            logger.error(f"HTTP Exception during sign in: {str(he)}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error during sign in: {str(e)}", exc_info=True)
            raise HTTPException(status_code=401, detail=str(e))

    @staticmethod
    def sign_in_with_google(credential: str, nonce: Optional[str] = None) -> Session:
        """Signs in or signs up a user with Google credentials."""
        try:
            # Sign in with Google using same pattern as password auth
            auth_response = auth.sign_in_with_password({"email": credential, "password": "", "provider": "google"})  # Google OAuth token as email  # Empty password for OAuth

            if not auth_response.session:
                raise HTTPException(status_code=401, detail="Invalid Google credentials")

            return auth_response.session

        except Exception as e:
            logger.error(f"Google sign in failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))

    @staticmethod
    def refresh_token(refresh_token: str) -> Session:
        """Refreshes the session tokens using the provided refresh token."""
        try:
            logging.debug(f"Received Refresh Token: {refresh_token}")

            if not refresh_token:
                logging.warning("No refresh token provided in the request")
                return {"error": "Refresh token is required"}, 400

            # Define the URL for Supabase's token refresh endpoint
            token_url = f"{supabase.supabase_url}/auth/v1/token?grant_type=refresh_token"

            # Set headers for the request
            headers = {
                "Content-Type": "application/json",
                "apikey": supabase.supabase_key,
                "Authorization": f"Bearer {supabase.supabase_key}",
            }

            # Make the request to the Supabase token endpoint
            response = requests.post(token_url, json={"refresh_token": refresh_token}, headers=headers)

            logging.debug(f"Supabase Response Status: {response.status_code}")
            logging.debug(f"Supabase Response Body: {response.text}")

            if response.status_code == 200:
                # Convert raw JSON response to AuthResponse model to match return type
                auth_response = AuthResponse.model_validate(response.json())

                logging.debug("Session refreshed successfully")
                return auth_response
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

            user_response = supabase.auth.get_user(access_token)
            return user_response

        except Exception as e:
            logging.error(f"Error retrieving current user: {e}")
            raise

    @staticmethod
    def request_password_reset(email: str):
        try:
            # Send password reset email
            auth.reset_password_email(email)
            return {"message": "Password reset email sent"}
        except Exception as e:
            logger.error(f"Password reset request failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def reset_password(access_token: str, new_password: str):
        try:
            # Update password with token
            auth.update_user(access_token, {"password": new_password})
            return {"message": "Password updated successfully"}
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
