# models/renter.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Guest(BaseModel):
    id: UUID
    phone: str
    first_name: str
    last_name: Optional[str] = None
    created_at: str
    updated_at: str
