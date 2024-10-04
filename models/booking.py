# models/booking.py
# models/property.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Booking(BaseModel):
    id: str
    property_id: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat() if v else None}
