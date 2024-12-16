from typing import Optional, List
from pydantic import BaseModel


class Guest(BaseModel):
    """Model representing a guest in the system"""

    id: str = None
    phone: str = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    bookings: Optional[List["BookingGuest"]] = []


class CreateGuest(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateGuest(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
