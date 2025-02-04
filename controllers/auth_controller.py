# controllers/auth_controller.py

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from auth_utils import get_current_user
from services.auth_service import AuthService
from gotrue import AuthResponse, UserResponse, User, Session
from gotrue.types import Provider
from .inputs.auth_inputs import SignupInput, LoginInput, GoogleSignInInput, PasswordResetRequestInput, PasswordResetInput, RefreshTokenInput, OTPInput

# Configure logging
logger = logging.getLogger(__name__)

# Create router for auth-related routes
router = APIRouter(tags=["authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(data: SignupInput):
    """Signs up a new user."""
    try:
        response = AuthService.sign_up_with_email_and_password(email=data.email, password=data.password, phone=data.phone, first_name=data.first_name, last_name=data.last_name)
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Signup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh_token", response_model=Session, operation_id="refresh_token")
async def refresh_token(data: RefreshTokenInput):
    """Refreshes the session tokens using the provided refresh token."""
    try:
        return AuthService.refresh_token(data.refresh_token)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserResponse, operation_id="me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Retrieves the current logged-in user's information."""
    try:
        user_response = AuthService.get_current_user()
        return user_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logout", operation_id="logout")
async def logout():
    """Logs out the current user."""
    return AuthService.logout()


@router.post("/signin", response_model=Session)
async def login(data: LoginInput):
    """Logs in a user with email and password."""
    logger.info("Received login request")
    logger.debug(f"Login data: email={data.email[:3]}***, password=***")

    try:
        # Validate input
        if not data.email or not data.password:
            logger.error("Missing email or password")
            raise HTTPException(status_code=400, detail="Email and password are required")

        # Attempt login
        session = AuthService.sign_in_with_email_and_password(email=data.email, password=data.password)

        logger.info("Login successful")
        return session

    except HTTPException as he:
        logger.error(f"Login failed with HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Login failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google", response_model=Session, operation_id="google")
async def google_sign_in(data: GoogleSignInInput):
    """Signs in or signs up a user with Google credentials."""
    try:
        return AuthService.sign_in_with_google(data.credential, data.nonce)
    except Exception as e:
        logger.error(f"Google sign in failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request_password_reset", operation_id="request_password_reset")
async def request_password_reset(data: PasswordResetRequestInput):
    """Request a password reset link to be sent to email."""
    try:
        return AuthService.request_password_reset(email=data.email)
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset_password", operation_id="reset_password")
async def reset_password(data: PasswordResetInput):
    """Reset password using the token received via email."""
    try:
        if len(data.new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        return AuthService.reset_password(access_token=data.access_token, new_password=data.new_password)
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
