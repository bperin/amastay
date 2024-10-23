# models/renter.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Guest(BaseModel):
    id: str
    phone: str
    first_name: str
    last_name: str
    created_at: str
    updated_at: str
