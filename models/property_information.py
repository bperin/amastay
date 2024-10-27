# models/property_information.py

from pydantic import BaseModel, Field
from typing import Optional


class PropertyInformation(BaseModel):
    id: str
    property_id: Optional[str] = None
    name: Optional[str] = None
    detail: Optional[str] = None
    is_recommendation: Optional[bool] = None
    metadata_url: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
