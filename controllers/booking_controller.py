from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from models.booking_model import Booking, CreateBooking, UpdateBooking
from services.booking_service import BookingService
from auth_utils import get_current_user
import logging

router = APIRouter(tags=["bookings"])


@router.post("/create", response_model=Booking, status_code=201, operation_id="create_booking")
async def create_booking(data: CreateBooking, current_user: dict = Depends(get_current_user)):
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


@router.get("/list", response_model=List[Booking], operation_id="get_all_bookings")
async def list_bookings(current_user: dict = Depends(get_current_user)):
    """Lists all bookings"""
    try:
        bookings = BookingService.get_all_bookings_by_owner(current_user["id"])
        return bookings
    except Exception as e:
        logging.error(f"Error in list_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=List[Booking], operation_id="get_booking")
async def get_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieves a booking by its ID"""
    try:
        booking = BookingService.get_booking_by_manager(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except Exception as e:
        logging.error(f"Error in get_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update", response_model=Booking, operation_id="update_booking")
async def update_booking(data: UpdateBooking, current_user: dict = Depends(get_current_user)):
    """Updates a booking"""
    try:
        updated_booking = BookingService.update_booking(booking_id=str(data.booking_id), property_id=str(data.property_id) if data.property_id else None, check_in=data.check_in, check_out=data.check_out, notes=data.notes)
        if not updated_booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated_booking
    except Exception as e:
        logging.error(f"Error in update_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", operation_id="delete_booking")
async def delete_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    """Deletes a booking"""
    try:
        success = BookingService.delete_booking(str(booking_id))
        if success:
            return {"message": "Booking deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete booking")
    except Exception as e:
        logging.error(f"Error in delete_booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))
