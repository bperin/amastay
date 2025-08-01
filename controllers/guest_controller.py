from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Group model imports together
from models import *

# Group service imports together
from models.booking_guest_model import CreateBookingGuest
from models.guest_model import Guest
from services.guest_service import GuestService
from services.booking_service import BookingService
from services.pinpoint_service import PinpointService

from auth_utils import get_current_user
import logging
import os


router = APIRouter(tags=["booking_guests"])


@router.post("/create", response_model=Guest, operation_id="add_guest")
async def add_guest(data: CreateBookingGuest, current_user: dict = Depends(get_current_user)):
    """Add a guest to a booking"""
    try:
        # Create or get guest
        guest = GuestService.get_or_create_guest(data.phone, data.first_name, data.last_name)

        # Verify booking exists
        booking = BookingService.get_booking_by_id(data.booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Add guest to booking
        booking_guest = BookingService.add_guest(guest.id, booking.id)

        if booking_guest:
            # Send welcome message
            try:
                content = f"AmastayAI: You've been added to a reservation. " f"Reply YES to opt-in for updates about your stay. " f"Msg frequency varies. Msg & data rates may apply. " f"Text HELP for support, STOP to opt-out. " f"Booking ID: {data.booking_id}, " f"Guest: {data.first_name} {data.last_name or ''}"
                PinpointService.send_sms(data.phone, os.getenv("SYSTEM_PHONE_NUMBER"), content)
            except Exception as sms_error:
                logging.error(f"Error sending welcome SMS: {sms_error}")

            return guest.model_dump()
        raise HTTPException(status_code=400, detail="Failed to add guest")

    except Exception as e:
        logging.error(f"Error in add_guest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{booking_guest_id}", operation_id="remove_guest_from_booking")
async def remove_guest(booking_guest_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a guest from a booking"""
    try:
        success = GuestService.remove_booking_guest(booking_guest_id)
        if success:
            return {"message": "Guest removed successfully"}
        raise HTTPException(status_code=400, detail="Failed to remove guest")
    except Exception as e:
        logging.error(f"Error in remove_guest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guests/{booking_id}", response_model=List[Guest], operation_id="get_guests_for_booking")
async def get_guests(booking_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a guest from a booking"""
    try:
        guests = GuestService.get_guests_by_booking(booking_id)
        if not guests:
            return []
        return [guest.model_dump() for guest in guests]
    except Exception as e:
        logging.error(f"Error in remove_guest: {e}")
        raise HTTPException(status_code=500, detail=str(e))
