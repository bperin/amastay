from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
from datetime import datetime


class Manager(BaseModel):
    id: str
    owner_id: str
    property_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    created_at: str
    updated_at: str
