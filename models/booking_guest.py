# models/booking_guest.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

from models.booking import Booking
from models.guest import Guest


class BookingGuest(BaseModel):
    id: UUID
    booking_id: UUID
    guest_id: UUID
    created_at: str
    updated_at: str

    booking: Optional[Booking] = None
    guest: Optional[Guest] = None
