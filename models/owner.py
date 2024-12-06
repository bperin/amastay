# models/owner.py

from pydantic import BaseModel
from typing import Optional


class Owner(BaseModel):
    id: str
    phone: str
    bio: Optional[str] = None
    first_name: str
    last_name: str
    created_at: str
    updated_at: str
