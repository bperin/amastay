# models/owner.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Owner(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    phone: str
    bio: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
