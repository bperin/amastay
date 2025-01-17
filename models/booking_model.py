from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from models import *


class Guest(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None


class Booking(BaseModel):
    """Model representing a booking in the system"""

    id: str = ""
    property_id: str = ""
    check_in: str = ""
    check_out: str = ""
    notes: Optional[str] = None
    guests: List[Guest] = []
    created_at: str = ""
    updated_at: str

    # Relationships
    property_: Optional[Property] = Field(default=None, alias="property")
    messages: Optional[List[Message]] = None


class CreateBooking(BaseModel):
    property_id: str = ""
    check_in: str = ""
    check_out: str = ""
    notes: Optional[str] = None
    guests: List[Guest] = []


class UpdateBooking(BaseModel):
    notes: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
