# models/property.py

from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class Property(BaseModel):
    id: Optional[UUID]
    owner_id: Optional[str]  # Assuming owner_id is a string (user's ID)
    name: str
    description: Optional[str]
    address: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    property_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
