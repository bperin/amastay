# controllers/auth_controller.py

from flask import Blueprint, request, jsonify
from auth_utils import jwt_required
from services.auth_service import AuthService
import logging
import time

# Create a Blueprint for the auth routes
auth_bp = Blueprint("auth_bp", __name__)


# Sign-Up Route
@auth_bp.route("/signup", methods=["POST"])
def signup():
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
        logging.warning("Signup failed: Missing required fields.")
        return jsonify({"error": "All fields are required"}), 400

    # Call the AuthService to handle sign-up
    return AuthService.signup(
        phone_number,
        first_name,
        last_name,
        estimated_properties,
    )


# OTP Verification Route
@auth_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    """
    Verifies the OTP received by the user and issues session tokens.
    Expects JSON data with phone_number and otp.
    """
    data = request.get_json()
    phone_number = data.get("phone_number")
    otp = data.get("otp")

    if not all([phone_number, otp]):
        logging.warning("OTP verification failed: Missing phone number or OTP.")
        return jsonify({"error": "Phone number and OTP are required"}), 400

    print(phone_number, otp)
    # Call the AuthService to handle OTP verification
    return AuthService.verify_otp(phone_number, otp)


# Refresh Token Route
@auth_bp.route("/refresh_token", methods=["POST"])
def refresh_token():
    """
    Refreshes the session tokens using the provided refresh token.
    Expects JSON data with refresh_token.
    """
    return AuthService.refresh_token()


# Get Current User Route
@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    """
    Retrieves the current logged-in user's information.
    Requires Authorization header with Bearer token.
    """
    return AuthService.get_current_user()


@auth_bp.route("/logout", methods=["GET"])
def logout():
    return AuthService.logout()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Sends a sms OTP
    """
    data = request.get_json()
    phone_number = data.get("phone_number")

    if not phone_number:
        logging.warning("Logout failed: Missing phone_number.")
        return jsonify({"error": "phone_number is required"}), 400

    return AuthService.login(phone_number)


@auth_bp.route("/resend", methods=["POST"])
def resend():
    """
    resend account creation sms OTP
    """
    data = request.get_json()
    phone_number = data.get("phone_number")

    if not phone_number:
        logging.warning("Logout failed: Missing phone_number.")
        return jsonify({"error": "phone_number is required"}), 400

    return AuthService.resend_otp(phone_number)
