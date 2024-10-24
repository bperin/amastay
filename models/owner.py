# models/owner.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Owner(BaseModel):
    id: str
    phone: str
    bio: Optional[str]
    first_name: str
    last_name: str
    created_at: str
    updated_at: str
