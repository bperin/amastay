# models/document.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Document(BaseModel):
    id: UUID
    property_id: Optional[UUID]
    file_url: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
