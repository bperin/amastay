# models/property.py


from pydantic import BaseModel, Field
from typing import Optional

class Property(BaseModel):
    id: Optional[str] = Field(default=None)
    owner_id: Optional[str] = Field(default=None)  # Assuming owner_id is a string (user's ID)
    name: str
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    lat: Optional[float] = Field(default=None)
    lng: Optional[float] = Field(default=None)
    property_url: Optional[str] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)
