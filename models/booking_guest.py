# models/booking_guest.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BookingGuest(BaseModel):
    id: str
    booking_id: str
    guest_id: str
    created_at: str
    updated_at: str
