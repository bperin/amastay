# controllers/auth_controller.py

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from auth_utils import get_current_user
from models.owner import Owner
from services.auth_service import AuthService
from gotrue import AuthResponse, UserResponse, User, Session
from gotrue.types import Provider
from .inputs.auth_inputs import SignupInput, LoginInput, GoogleSignInInput, PasswordResetRequestInput, PasswordResetInput, RefreshTokenInput, OTPInput

# Configure logging
logger = logging.getLogger(__name__)

# Create router for auth-related routes
router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(data: SignupInput):
    """Signs up a new user and sends an OTP to their phone number."""
    try:
        # Call the AuthService to handle sign-up
        user = AuthService.sign_up_with_email_and_password(first_name=data.first_name, last_name=data.last_name, email=data.email, password=data.password, phone=data.phone, user_type="owner")
        return user
    except ValueError as ve:
        logger.warning(f"Signup failed: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in signup: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/refresh_token", response_model=Session)
async def refresh_token(data: RefreshTokenInput):
    """Refreshes the session tokens using the provided refresh token."""
    try:
        return AuthService.refresh_token(data.refresh_token)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Retrieves the current logged-in user's information."""
    try:
        user_response = AuthService.get_current_user()
        return user_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logout")
async def logout():
    """Logs out the current user."""
    return AuthService.logout()


@router.post("/signin", response_model=Session)
async def login(data: LoginInput):
    """Logs in a user with email and password."""
    try:
        return AuthService.sign_in_with_email_and_password(data.email, data.password)
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google", response_model=Session)
async def google_sign_in(data: GoogleSignInInput):
    """Signs in or signs up a user with Google credentials."""
    try:
        return AuthService.sign_in_with_google(data.credential, data.nonce)
    except Exception as e:
        logger.error(f"Google sign in failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequestInput):
    """Request a password reset link to be sent to email."""
    try:
        return AuthService.request_password_reset(email=data.email)
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
async def reset_password(data: PasswordResetInput):
    """Reset password using the token received via email."""
    try:
        if len(data.new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        return AuthService.reset_password(access_token=data.access_token, new_password=data.new_password)
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
