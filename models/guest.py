# models/renter.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Guest(BaseModel):
    id: UUID
    phone: str
    full_name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
