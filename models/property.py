# models/property.py

from pydantic import BaseModel, Field
from typing import Optional


class Property(BaseModel):
    id: str = Field(default=None)
    owner_id: str = Field(default=None)
    name: str
    description: str = Field(default=None)
    address: str = Field(default=None)
    lat: float = Field(default=None)
    lng: float = Field(default=None)
    property_url: str = Field(default=None)
    created_at: str = Field(default=None)
    updated_at: str = Field(default=None)
