from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from models.owner import Owner


class Manager(BaseModel):
    id: UUID
    owner_id: UUID
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: str
    updated_at: str

    owner: Optional[Owner] = None
