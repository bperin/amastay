# controllers/auth_controller.py

from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from auth_utils import jwt_required
from services.auth_service import AuthService
import logging
import time

try:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
except Exception as e:
    print(f"Error setting up logging: {str(e)}")

ns_auth = Namespace("authentication", description="Authentication operations")

# Define models for request/response
signup_model = ns_auth.model(
    "Signup",
    {
        "first_name": fields.String(
            required=True, description="First name", type="string"
        ),
        "last_name": fields.String(
            required=True, description="Last name", type="string"
        ),
        "estimated_properties": fields.Integer(
            required=True, description="Estimated number of properties", type="integer"
        ),
        "phone_number": fields.String(
            required=True, description="Phone number", type="string"
        ),
    },
)

otp_model = ns_auth.model(
    "OTP",
    {
        "phone_number": fields.String(required=True, description="Phone number"),
        "otp": fields.String(required=True, description="One-time password"),
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
    {"phone_number": fields.String(required=True, description="Phone number")},
)


# Sign-Up Route
@ns_auth.route("/signup")
class Signup(Resource):
    @ns_auth.expect(signup_model)
    def post(self):
        """
        Signs up a new user and sends an OTP to their phone number.
        Expects JSON data with first_name, last_name, estimated_properties, and phone_number.
        """
        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        estimated_properties = data.get("estimated_properties")
        phone_number = data.get("phone_number")

        # Validate required fields
        if not all([first_name, last_name, estimated_properties, phone_number]):
            try:
                logger.warning("Signup failed: Missing required fields.")
            except Exception as e:
                print(f"Error logging warning: {str(e)}")
            return {"error": "All fields are required"}, 400

        # Call the AuthService to handle sign-up
        return AuthService.signup(
            phone_number,
            first_name,
            last_name,
            estimated_properties,
        )


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
        phone_number = data.get("phone_number")
        otp = data.get("otp")

        if not all([phone_number, otp]):
            try:
                logger.warning("OTP verification failed: Missing phone number or OTP.")
            except Exception as e:
                print(f"Error logging warning: {str(e)}")
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
    def get(self):
        """
        Retrieves the current logged-in user's information.
        Requires Authorization header with Bearer token.
        """
        user_response = AuthService.get_current_user()
        if "error" in user_response:
            return user_response.model_dump(), 500
        else:
            return user_response.user.model_dump_json(), 200


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
        phone_number = data.get("phone_number")

        if not phone_number:
            try:
                logger.warning("Login failed: Missing phone_number.")
            except Exception as e:
                print(f"Error logging warning: {str(e)}")
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
        phone_number = data.get("phone_number")

        if not phone_number:
            try:
                logger.warning("Resend OTP failed: Missing phone_number.")
            except Exception as e:
                print(f"Error logging warning: {str(e)}")
            return {"error": "phone_number is required"}, 400

        return AuthService.resend_otp(phone_number)
