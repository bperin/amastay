from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from models import *
from datetime import datetime
from models.guest_model import Guest  # Import existing Guest model


class Booking(BaseModel):
    """Model representing a booking in the system"""

    id: Optional[str]
    property_id: str
    user_id: str
    check_in: datetime
    check_out: datetime
    guests: int  # Number of guests
    total_price: float
    status: str  # pending, confirmed, cancelled
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    # Optional relationships
    property_: Optional[Property] = Field(default=None, alias="property")
    messages: Optional[List[Message]] = None


class CreateBooking(BaseModel):
    """Input model for creating a booking"""

    property_id: str
    check_in: datetime
    check_out: datetime
    total_price: float


class UpdateBooking(BaseModel):
    """Input model for updating a booking"""

    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    guest_count: Optional[int] = None
    status: Optional[str] = None


class BookingDetailsResponse(BaseModel):
    booking: Booking
    property_details: dict  # Property details can be added as needed
