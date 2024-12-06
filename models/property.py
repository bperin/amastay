# models/property.py

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from models.owner import Owner
from models.manager import Manager


class Property(BaseModel):
    id: str
    owner_id: str
    manager_id: Optional[str] = None
    name: str
    description: str
    address: str
    lat: float
    lng: float
    property_url: str
    created_at: str
    updated_at: str

    owner: Optional[Owner] = None
    manager: Optional[Manager] = None
