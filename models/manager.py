from typing import Optional
from pydantic import BaseModel

from models.owner import Owner


class Manager(BaseModel):
    id: str
    owner_id: str
    first_name: str
    email: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    active: bool = False
    phone_verified: bool = False
    created_at: str
    updated_at: str

    owner: Optional[Owner] = None
