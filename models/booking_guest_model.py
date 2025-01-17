from typing import Optional
from pydantic import BaseModel, Field
from models import *


class BookingGuest(BaseModel):
    """Association model between bookings and guests"""

    id: str = ""
    booking_id: str = ""
    guest_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Relationships with Field alias
    booking: Optional["Booking"] = Field(default=None)
    guest: Optional["Guest"] = Field(default=None)


class CreateBookingGuest(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    booking_id: str


class UpdateBookingGuest(BaseModel):
    booking_id: Optional[str] = None
    guest_id: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
