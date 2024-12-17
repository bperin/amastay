# models/property_information.py

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class PropertyInformation(BaseModel):
    """Model representing property information details"""

    id: str = ""
    name: str = ""
    detail: str = ""
    is_recommendation: bool = False
    metadata_url: str = ""
    category: str = ""
    property_id: Optional[str] = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    property_: Optional["Property"] = Field(default=None, alias="property")


class CreatePropertyInformation(BaseModel):
    property_id: str
    name: str
    detail: Optional[str] = None
    is_recommendation: bool = False
    metadata_url: Optional[str] = None


class UpdatePropertyInformation(BaseModel):
    id: str
    name: Optional[str] = None
    detail: Optional[str] = None
    is_recommendation: Optional[bool] = None
    metadata_url: Optional[str] = None
    category: Optional[str] = None
