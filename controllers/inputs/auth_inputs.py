from flask_restx import fields


def get_auth_input_models(ns_auth):
    """Define input models for auth endpoints"""

    signup_model = ns_auth.model(
        "Signup",
        {
            "first_name": fields.String(required=True, description="First name"),
            "last_name": fields.String(required=True, description="Last name"),
            "email": fields.String(required=True, description="Email"),
            "phone": fields.String(required=True, description="Phone"),
            "password": fields.String(required=True, description="Password"),
        },
    )

    otp_model = ns_auth.model(
        "OTP",
        {
            "phone": fields.String(required=True, description="Phone number"),
            "otp": fields.String(required=True, description="One-time password"),
        },
    )

    refresh_token_model = ns_auth.model(
        "RefreshToken",
        {
            "refresh_token": fields.String(required=True, description="Refresh token"),
        },
    )

    login_model = ns_auth.model(
        "Login",
        {"email": fields.String(required=True, description="User email"), "password": fields.String(required=True, description="User password")},
    )

    google_signin_model = ns_auth.model(
        "GoogleSignIn",
        {"credential": fields.String(required=True, description="Google ID token"), "nonce": fields.String(required=False, description="Optional nonce for verification")},
    )

    password_reset_request_model = ns_auth.model("PasswordResetRequest", {"email": fields.String(required=True, description="User email")})

    password_reset_model = ns_auth.model("PasswordReset", {"access_token": fields.String(required=True, description="Reset password token"), "new_password": fields.String(required=True, description="New password")})

    return {"signup_model": signup_model, "otp_model": otp_model, "login_model": login_model, "google_signin_model": google_signin_model, "password_reset_request_model": password_reset_request_model, "password_reset_model": password_reset_model, "refresh_token_model": refresh_token_model}
