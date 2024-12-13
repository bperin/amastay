from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.user_service import UserService
from auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class ProfileUpdate(BaseModel):
    first_name: str
    last_name: str


class PhoneUpdate(BaseModel):
    phone_number: str


class UserProfile(BaseModel):
    id: str
    email: str
    phone: Optional[str] = None
    metadata: Dict[str, Any]


@router.get("/profile", response_model=UserProfile, operation_id="get_profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    return UserService.get_user_profile(current_user["id"])


@router.put("/profile", operation_id="update_profile")
async def update_profile(data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Update user profile information"""
    return UserService.update_user_profile(current_user["id"], data.dict())


@router.post("/phone", operation_id="add_phone")
async def add_phone(data: PhoneUpdate, current_user: dict = Depends(get_current_user)):
    """Add or update phone number"""
    return UserService.add_phone_number(current_user["id"], data.phone_number)
