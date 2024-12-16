# models/owner_model.py
from typing import Optional, List
from pydantic import BaseModel


class Owner(BaseModel):
    """Owner model representing property owners"""

    id: str = None
    phone: str = None
    bio: Optional[str] = None
    first_name: str = None
    last_name: str = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    properties: Optional[List["Property"]] = None


class CreateOwner(BaseModel):
    phone: str
    first_name: str
    last_name: str
    bio: Optional[str] = None


class UpdateOwner(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
