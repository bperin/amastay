# models/booking.py
# models/property.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Booking(BaseModel):
    id: str
    property_id: str
    check_in: str
    check_out: str
    created_at: str
    updated_at: str
