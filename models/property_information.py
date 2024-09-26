# models/property_information.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class PropertyInformation(BaseModel):
    id: UUID
    property_id: Optional[UUID]
    detail: Optional[str]
    video_url: Optional[str]
    category: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
