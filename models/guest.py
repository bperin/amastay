# models/renter.py

from pydantic import BaseModel
from typing import Optional


class Guest(BaseModel):
    id: str
    phone: str
    first_name: str
    last_name: Optional[str] = None
    created_at: str
    updated_at: str
