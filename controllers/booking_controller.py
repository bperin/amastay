from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from models.booking import Booking
from services.booking_service import BookingService
from auth_utils import get_current_user
import logging


router = APIRouter(prefix="/bookings", tags=["bookings"])


class GuestInput(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: str


class CreateBookingInput(BaseModel):
    property_id: UUID
    notes: Optional[str] = None
    check_in: datetime
    check_out: datetime
    guests: Optional[List[GuestInput]] = None


class UpdateBookingInput(BaseModel):
    booking_id: UUID
    property_id: Optional[UUID] = None
    notes: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None


@router.post("/create", response_model=Booking, status_code=201)
async def create_booking(data: CreateBookingInput, current_user: dict = Depends(get_current_user)):
    """Creates a new booking"""
    try:
        new_booking = BookingService.create_booking(property_id=str(data.property_id), check_in=data.check_in, check_out=data.check_out, notes=data.notes, guests=data.guests)
        return new_booking
    except ValueError as ve:
        logging.error(f"Validation error in create_booking: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in create_booking: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/list", response_model=List[Booking])
async def list_bookings(current_user: dict = Depends(get_current_user)):
    """Lists all bookings"""
    try:
        bookings = BookingService.get_all_bookings_by_owner(current_user["id"])
        return bookings
    except Exception as e:
        logging.error(f"Error in list_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list_details", response_model=List[Booking])
async def list_bookings_with_details(current_user: dict = Depends(get_current_user)):
    """Lists all bookings with details"""
    try:
        bookings = BookingService.get_bookings_by_owner_with_details(current_user["id"])
        return bookings
    except Exception as e:
        logging.error(f"Error in list_bookings_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: UUID, current_user: dict = Depends(get_current_user)):
    """Retrieves a booking by its ID"""
    try:
        booking = BookingService.get_booking_by_manager(str(booking_id))
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except Exception as e:
        logging.error(f"Error in get_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update", response_model=Booking)
async def update_booking(data: UpdateBookingInput, current_user: dict = Depends(get_current_user)):
    """Updates a booking"""
    try:
        updated_booking = BookingService.update_booking(booking_id=str(data.booking_id), property_id=str(data.property_id) if data.property_id else None, check_in=data.check_in, check_out=data.check_out, notes=data.notes)
        if not updated_booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated_booking
    except Exception as e:
        logging.error(f"Error in update_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}")
async def delete_booking(booking_id: UUID, current_user: dict = Depends(get_current_user)):
    """Deletes a booking"""
    try:
        success = BookingService.delete_booking(str(booking_id))
        if success:
            return {"message": "Booking deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete booking")
    except Exception as e:
        logging.error(f"Error in delete_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/property/{property_id}", response_model=List[Booking])
async def get_property_bookings(property_id: UUID, current_user: dict = Depends(get_current_user)):
    """Retrieves all bookings for a specific property"""
    try:
        bookings = BookingService.get_bookings_by_property_id(str(property_id))
        return bookings
    except Exception as e:
        logging.error(f"Error in get_property_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/details/{booking_id}", response_model=BookingWithDetails)
async def get_booking_details(booking_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get a booking with its property and guest details"""
    try:
        booking_details = BookingService.get_booking_with_details(str(booking_id))
        if not booking_details:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking_details
    except Exception as e:
        logging.error(f"Error in get_booking_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming")
async def get_upcoming_booking(phone: str, current_user: dict = Depends(get_current_user)):
    """Get the next upcoming booking for a guest by their phone number"""
    try:
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required")

        booking = BookingService.get_next_upcoming_booking_by_phone(phone)
        if not booking:
            raise HTTPException(status_code=404, detail="No upcoming bookings found")
        return {"booking": booking}
    except Exception as e:
        logging.error(f"Error in get_upcoming_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guest/{guest_id}", response_model=Booking)
async def get_guest_booking(guest_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get the next booking for a specific guest by their ID"""
    try:
        booking = BookingService.get_next_booking_by_guest_id(str(guest_id))
        if not booking:
            raise HTTPException(status_code=404, detail="No bookings found for this guest")
        return booking
    except Exception as e:
        logging.error(f"Error in get_guest_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))
