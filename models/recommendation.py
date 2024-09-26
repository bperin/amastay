# models/recommendation.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Recommendation(BaseModel):
    id: UUID
    property_id: Optional[UUID]
    owner_id: Optional[UUID]
    detail: Optional[str]
    category: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
