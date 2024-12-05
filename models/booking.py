import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from models.property import Property


class Booking(BaseModel):
    id: UUID
    property_id: UUID
    notes: Optional[str] = None
    check_in: str
    check_out: str
    created_at: str
    updated_at: str

    property: Optional[Property] = None
