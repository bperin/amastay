# controllers/auth_controller.py

from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from auth_utils import jwt_required
from models.owner import Owner
from models.to_swagger import pydantic_to_swagger_model
from services.auth_service import AuthService
import logging
import time
from gotrue import AuthResponse, UserResponse, User
from gotrue.types import Provider
from .inputs.auth_inputs import get_auth_input_models

# Configure logging
logger = logging.getLogger(__name__)

ns_auth = Namespace("authentication", description="Authentication operations")

# Define shared auth response model


# Get input models from auth_inputs
signup_input_model = get_auth_input_models(ns_auth)["signup_model"]
login_input_model = get_auth_input_models(ns_auth)["login_model"]
google_signin_input_model = get_auth_input_models(ns_auth)["google_signin_model"]
password_reset_input_request_model = get_auth_input_models(ns_auth)["password_reset_request_model"]
password_reset_input_model = get_auth_input_models(ns_auth)["password_reset_model"]
otp_input_model = get_auth_input_models(ns_auth)["otp_model"]

# Add debug logging for model registration
auth_response_model = pydantic_to_swagger_model(ns_auth, "AuthResponse", AuthResponse)
user_response_model = pydantic_to_swagger_model(ns_auth, "UserReponse", UserResponse)


# Sign-Up Route
@ns_auth.route("/signup")
class Signup(Resource):
    @ns_auth.expect(signup_input_model)
    @ns_auth.response(200, "Success", auth_response_model)
    @ns_auth.response(400, "Invalid request")
    @ns_auth.response(500, "Internal server error")
    def post(self):
        """
        Signs up a new user and sends an OTP to their phone number.
        Expects JSON data with first_name, last_name, email, password, and phone_number.
        """
        data = request.get_json()

        # Sanitize and validate required fields
        required_fields = ["first_name", "last_name", "email", "password", "phone"]
        errors = {}

        for field in required_fields:
            value = data.get(field, "").strip()
            if not value:
                errors[field] = f"{field.replace('_', ' ').title()} is required"
            data[field] = value

        if errors:
            logger.warning(f"Signup failed: {errors}")
            return {"errors": errors}, 400

        # Add basic password validation
        if len(data.get("password", "")) < 8:
            return {"error": "Password must be at least 8 characters long"}, 400

        # Call the AuthService to handle sign-up
        user = AuthService.sign_up_with_email_and_password(first_name=data["first_name"], last_name=data["last_name"], email=data["email"], password=data["password"], phone=data["phone"], user_type="owner")
        return user.model_dump(), 200


# Refresh Token Route
@ns_auth.route("/refresh_token")
class RefreshToken(Resource):
    @ns_auth.response(200, "Success", auth_response_model)
    @ns_auth.response(400, "Bad Request")
    def post(self):
        """
        Refreshes the session tokens using the provided refresh token.
        Expects JSON data with refresh_token.
        """
        return AuthService.refresh_token()


@ns_auth.route("/me")
class GetCurrentUser(Resource):
    @jwt_required
    @ns_auth.response(200, "Success", user_response_model)
    @ns_auth.response(400, "Bad Request")
    @ns_auth.response(500, "Internal server error")
    def get(self):
        """
        Retrieves the current logged-in user's information.
        Requires Authorization header with Bearer token.
        """
        try:
            user_response = AuthService.get_current_user()
            return user_response.model_dump(), 200
        except Exception as e:
            return {"error": str(e)}, 500


@ns_auth.route("/logout")
class Logout(Resource):
    def get(self):
        return AuthService.logout()


@ns_auth.route("/signin")
class Login(Resource):
    @ns_auth.expect(login_input_model)
    @ns_auth.response(200, "Success", auth_response_model)
    @ns_auth.response(400, "Bad Request")
    @ns_auth.response(500, "Internal server error")
    def post(self):
        """
        Logs in a user with email and password.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            breakpoint()
            if not email or not password:
                logger.warning("Login failed: Missing email or password.")
                return {"error": "Email and password are required"}, 400

            return AuthService.sign_in_with_email_and_password(email, password)
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"error": str(e)}, 500


@ns_auth.route("/google")
class GoogleSignIn(Resource):
    @ns_auth.expect(google_signin_input_model)
    @ns_auth.response(200, "Success", auth_response_model)
    @ns_auth.response(400, "Invalid request")
    @ns_auth.response(500, "Server error")
    @ns_auth.doc(description="Sign in with Google")
    def post(self):
        """
        Signs in or signs up a user with Google credentials
        """
        try:
            data = request.get_json()
            credential = data.get("credential")
            nonce = data.get("nonce")  # Optional

            if not credential:
                return {"error": "Google credential is required"}, 400

            return AuthService.sign_in_with_google(credential, nonce)
        except Exception as e:
            logger.error(f"Google sign in failed: {e}")
            return {"error": str(e)}, 500


@ns_auth.route("/request-password-reset")
class RequestPasswordReset(Resource):
    @ns_auth.expect(password_reset_input_request_model)
    @ns_auth.doc(responses={200: "Success", 400: "Invalid request"})
    def post(self):
        """
        Request a password reset link to be sent to email
        """
        data = request.get_json()
        email = data.get("email")

        if not email:
            return {"error": "Email is required"}, 400

        try:
            return AuthService.request_password_reset(email=email)
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            return {"error": str(e)}, 400


@ns_auth.route("/reset-password")
class ResetPassword(Resource):
    @ns_auth.expect(password_reset_input_model)
    @ns_auth.doc(responses={200: "Success", 400: "Invalid request"})
    def post(self):
        """
        Reset password using the token received via email
        """
        data = request.get_json()
        access_token = data.get("access_token")
        new_password = data.get("new_password")

        if not access_token or not new_password:
            return {"error": "Access token and new password are required"}, 400

        if len(new_password) < 8:
            return {"error": "Password must be at least 8 characters long"}, 400

        try:
            return AuthService.reset_password(access_token=access_token, new_password=new_password)
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {"error": str(e)}, 400
