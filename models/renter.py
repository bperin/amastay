# models/renter.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Renter(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    phone: str
    full_name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
