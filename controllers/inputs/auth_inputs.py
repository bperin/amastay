from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupInput(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str

    class Config:
        json_schema_extra = {"example": {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "phone": "+1234567890", "password": "securepassword123"}}


class OTPInput(BaseModel):
    phone: str
    otp: str

    class Config:
        json_schema_extra = {"example": {"phone": "+1234567890", "otp": "123456"}}


class RefreshTokenInput(BaseModel):
    refresh_token: str

    class Config:
        json_schema_extra = {"example": {"refresh_token": "your.refresh.token"}}


class LoginInput(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {"example": {"email": "john.doe@example.com", "password": "securepassword123"}}


class GoogleSignInInput(BaseModel):
    credential: str
    nonce: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {"credential": "google.id.token", "nonce": "optional_nonce_value"}}


class PasswordResetRequestInput(BaseModel):
    email: str

    class Config:
        json_schema_extra = {"example": {"email": "john.doe@example.com"}}


class PasswordResetInput(BaseModel):
    access_token: str
    new_password: str

    class Config:
        json_schema_extra = {"example": {"access_token": "reset.token.value", "new_password": "newSecurePassword123"}}
