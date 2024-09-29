# models/booking_guest.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BookingGuest(BaseModel):
    id: UUID
    booking_id: Optional[UUID]
    guest_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
