from typing import Optional, List
from pydantic import BaseModel


class Property(BaseModel):
    """Property model representing real estate properties"""

    id: str = ""
    name: str = ""
    description: Optional[str] = ""
    address: str = ""
    lat: Optional[float] = 0.0
    lng: Optional[float] = 0.0
    property_url: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata_progress: int = 0

    # Foreign key references
    owner_id: str = ""
    manager_id: Optional[str] = ""
    metadata_id: Optional[str] = ""

    # Relationships (using forward refs)
    owner: Optional["Owner"] = None
    manager: Optional["Manager"] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class CreateProperty(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    property_url: str


class UpdateProperty(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[str] = None
    address: Optional[str] = None
    property_url: Optional[str] = None
