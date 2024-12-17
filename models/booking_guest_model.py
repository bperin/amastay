from typing import Optional
from pydantic import BaseModel
from models import *


class BookingGuest(BaseModel):
    """Association model between bookings and guests"""

    id: str = None
    booking_id: str = None
    guest_id: str = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    booking: Optional["Booking"] = None
    guest: Optional["Guest"] = None


class CreateBookingGuest(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    booking_id: str
    guest_id: str


class UpdateBookingGuest(BaseModel):
    booking_id: Optional[str] = None
    guest_id: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
