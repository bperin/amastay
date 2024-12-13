from ast import List
import logging
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, Callable
from functools import wraps
import os
import jwt
from jwt import PyJWTError
from auth_utils import get_current_user, require_admin_and_owner, require_admin_or_owner, require_admin
from models.booking import Booking
from services.booking_service import BookingService


# Create router
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/bookings/list", response_model=List[Booking], operation_id="get_all_bookings")
@require_admin
async def list_bookings(current_user: dict = Depends(get_current_user)):
    """Lists all bookings as an admin"""
    try:
        bookings = BookingService.get_all_bookings_as_admin()
        return bookings
    except Exception as e:
        logging.error(f"Error in list_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
