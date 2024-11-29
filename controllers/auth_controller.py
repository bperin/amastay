# controllers/auth_controller.py

from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from auth_utils import jwt_required
from models.owner import Owner
from services.auth_service import AuthService
import logging
import time
from gotrue import UserResponse
from gotrue.types import Provider
from .inputs.auth_inputs import get_auth_input_models

# Configure logging
logger = logging.getLogger(__name__)

ns_auth = Namespace("authentication", description="Authentication operations")

# Define shared auth response model
auth_response = ns_auth.response(
    200,
    "Success",
    otp_response,
    headers={
        "x-access-token": {"description": "Access token", "type": "string"},
        "x-refresh-token": {"description": "Refresh token", "type": "string"},
        "x-expires-at": {
            "description": "Token expiration timestamp",
            "type": "integer",
        },
        "x-user-id": {"description": "User ID", "type": "string"},
    },
)

auth_input_models = get_auth_input_models(ns_auth)

signup_model = auth_input_models["signup_model"]
otp_model = auth_input_models["otp_model"]
login_model = auth_input_models["login_model"]
google_signin_model = auth_input_models["google_signin_model"]
password_reset_request_model = auth_input_models["password_reset_request_model"]
password_reset_model = auth_input_models["password_reset_model"]


# Sign-Up Route
@ns_auth.route("/signup")
class Signup(Resource):
    @ns_auth.expect(signup_model)
    def post(self):
        """
        Signs up a new user and sends an OTP to their phone number.
        Expects JSON data with first_name, last_name, email, password, and phone_number.
        """
        data = request.get_json()

        # Extract fields with proper default handling and sanitize
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        phone = data.get("phone", "").strip()
        # Set sanitized values back in the data object
        data["first_name"] = first_name
        data["last_name"] = last_name
        data["email"] = email
        data["password"] = password
        data["phone"] = phone

        print(f"first_name: {first_name}, last_name: {last_name}, email: {email}, password: {password}, phone: {phone}")
        # Validate each field individually for better error messages
        errors = {}
        if not first_name:
            errors["first_name"] = "First name is required"
        if not last_name:
            errors["last_name"] = "Last name is required"
        if not email:
            errors["email"] = "Email is required"
        if not password:
            errors["password"] = "Password is required"
        if not phone:
            errors["phone"] = "Phone is required"

        if errors:
            logger.warning(f"Signup failed: {errors}")
            return {"errors": errors}, 400

        # Add basic password validation
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters long"}, 400

        # Call the AuthService to handle sign-up
        return AuthService.signup(first_name=data["first_name"], last_name=data["last_name"], email=data["email"], password=data["password"], phone=data["phone"], user_type="owner")


# OTP Verification Route
@ns_auth.route("/verify_otp")
@auth_response
class VerifyOTP(Resource):
    @ns_auth.expect(otp_model)
    def post(self):
        """
        Verifies the OTP received by the user and issues session tokens.
        Expects JSON data with phone_number and otp.
        """
        data = request.get_json()
        phone_number = data.get("phone")
        otp = data.get("otp")

        if not all([phone_number, otp]):
            logger.warning("OTP verification failed: Missing phone number or OTP.")
            return {"error": "Phone number and OTP are required"}, 400

        # Call the AuthService to handle OTP verification
        return AuthService.verify_otp(phone_number, otp)


# Refresh Token Route
@ns_auth.route("/refresh_token")
@auth_response
class RefreshToken(Resource):
    def post(self):
        """
        Refreshes the session tokens using the provided refresh token.
        Expects JSON data with refresh_token.
        """
        return AuthService.refresh_token()


@ns_auth.route("/me")
class GetCurrentUser(Resource):
    @jwt_required
    @ns_auth.response(200, "Success", get_me_response)
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


@ns_auth.route("/login")
class Login(Resource):
    @ns_auth.expect(login_model)
    def post(self):
        """
        Logs in a user with email and password.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        breakpoint()
        if not email or not password:
            logger.warning("Login failed: Missing email or password.")
            return {"error": "Email and password are required"}, 400

        return AuthService.login(email, password)


@ns_auth.route("/resend")
class ResendOTP(Resource):
    @ns_auth.expect(login_model)
    def post(self):
        """
        Resend account creation SMS OTP
        """
        data = request.get_json()
        phone_number = data.get("phone")

        if not phone_number:
            logger.warning("Resend OTP failed: Missing phone_number.")
            return {"error": "phone_number is required"}, 400

        return AuthService.resend_otp(phone_number)


@ns_auth.route("/google")
class GoogleSignIn(Resource):
    @ns_auth.expect(google_signin_model)
    @ns_auth.doc(responses={200: "Success", 400: "Invalid request", 500: "Server error"}, description="Sign in with Google")
    def post(self):
        """
        Signs in or signs up a user with Google credentials
        """
        data = request.get_json()
        credential = data.get("credential")
        nonce = data.get("nonce")  # Optional

        if not credential:
            return {"error": "Google credential is required"}, 400

        return AuthService.sign_in_with_google(credential, nonce)


@ns_auth.route("/request-password-reset")
class RequestPasswordReset(Resource):
    @ns_auth.expect(password_reset_request_model)
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
    @ns_auth.expect(password_reset_model)
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
