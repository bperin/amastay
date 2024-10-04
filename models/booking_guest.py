# models/booking_guest.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BookingGuest(BaseModel):
    id: str
    booking_id: Optional[str]
    guest_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
