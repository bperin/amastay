# models/booking.py
# models/property.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Booking(BaseModel):
    id: UUID
    property_id: Optional[UUID]
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
