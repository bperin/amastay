# models/property.py

from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from models.owner import Owner
from models.manager import Manager


class Property(BaseModel):
    id: UUID
    owner_id: UUID
    manager_id: Optional[UUID] = None
    name: str
    description: str
    address: str
    lat: float
    lng: float
    property_url: str
    created_at: str
    updated_at: str

    owner: Optional[Owner]
    manager: Optional[Manager]
