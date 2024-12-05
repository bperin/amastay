# models/owner.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Owner(BaseModel):
    id: UUID
    phone: str
    bio: Optional[str] = None
    first_name: str
    last_name: str
    created_at: str
    updated_at: str
