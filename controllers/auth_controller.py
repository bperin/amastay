# controllers/auth_controller.py

from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from auth_utils import jwt_required
from models.owner import Owner
from services.auth_service import AuthService
import logging
import time
from gotrue import UserResponse

# Configure logging
logger = logging.getLogger(__name__)

ns_auth = Namespace("authentication", description="Authentication operations")

# Define models for request/response
signup_model = ns_auth.model(
    "Signup",
    {
        "first_name": fields.String(required=True, description="First name", type="string"),
        "last_name": fields.String(required=True, description="Last name", type="string"),
        "email": fields.String(required=True, description="Last name", type="string"),
        "password": fields.String(required=True, description="Password", type="string"),
        "phone": fields.String(required=True, description="Phone number", type="string"),
    },
)

otp_model = ns_auth.model(
    "OTP",
    {
        "phone": fields.String(required=True, description="Phone number"),
        "otp": fields.String(required=True, description="One-time password"),
    },
)
get_me_response = ns_auth.model(
    "GetMeResponse",
    {
        "id": fields.String(description="User ID"),
        "email": fields.String(description="User email"),
        "phone": fields.String(description="User phone number"),
        "created_at": fields.DateTime(description="Account creation timestamp"),
        "updated_at": fields.DateTime(description="Last update timestamp"),
        "confirmed_at": fields.DateTime(description="Email confirmation timestamp"),
        "last_sign_in_at": fields.DateTime(description="Last sign in timestamp"),
        "role": fields.String(description="User role"),
        "app_metadata": fields.Raw(description="Application metadata"),
        "user_metadata": fields.Raw(description="User metadata"),
        "identities": fields.List(fields.Raw, description="User identities"),
    },
)
otp_response = ns_auth.model(
    "OTPResponse",
    {
        "message": fields.String(description="Success message"),
    },
)


login_model = ns_auth.model(
    "Login",
    {"phone": fields.String(required=True, description="Phone number")},
)


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

        # Extract fields with proper default handling
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        phone_number = data.get("phone", "").strip()
        print(f"first_name: {first_name}, last_name: {last_name}, email: {email}, password: {password}, phone_number: {phone_number}")
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
        if not phone_number:
            errors["phone"] = "Phone number is required"

        if errors:
            logger.warning(f"Signup failed: {errors}")
            return {"errors": errors}, 400

        # Add basic password validation
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters long"}, 400

        # Call the AuthService to handle sign-up
        return AuthService.signup(first_name, last_name, email, password, phone_number)


# OTP Verification Route
@ns_auth.route("/verify_otp")
@ns_auth.response(
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
@ns_auth.response(
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
        Sends a SMS OTP for login
        """
        data = request.get_json()
        phone_number = data.get("phone")

        if not phone_number:
            logger.warning("Login failed: Missing phone_number.")
            return {"error": "phone_number is required"}, 400

        return AuthService.login(phone_number)


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
