from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from models import *


class Booking(BaseModel):
    """Model representing a booking in the system"""

    id: str = ""
    notes: Optional[str] = ""
    check_in: str = ""
    check_out: str = ""
    property_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Relationships
    property_: Optional[Property] = Field(default=None, alias="property")
    guests: Optional[List[BookingGuest]] = None
    messages: Optional[List[Message]] = None


class CreateBooking(BaseModel):
    notes: Optional[str] = None
    check_in: str
    check_out: str
    property_id: str


class UpdateBooking(BaseModel):
    notes: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
