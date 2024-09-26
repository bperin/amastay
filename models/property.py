# models/property.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Property(BaseModel):
    id: UUID
    owner_id: Optional[UUID]
    name: str
    description: Optional[str]
    address: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    property_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
