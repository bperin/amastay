# models/property_information.py

from pydantic import BaseModel, Field
from typing import Optional


class PropertyInformation(BaseModel):
    id: str
    property_id: Optional[str] = None
    detail: Optional[str] = None
    video_url: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
