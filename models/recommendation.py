# models/recommendation.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Recommendation(BaseModel):
    id: UUID
    property_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    detail: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat() if v else None}
