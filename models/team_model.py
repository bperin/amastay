from typing import Optional
from pydantic import BaseModel
from models.owner_model import Owner


class Team(BaseModel):
    id: str = None
    name: str = None
    owner_id: str = None
    description: str = None
    created_at: str = None
    updated_at: str = None

    owner: Optional[Owner] = None


class CreateTeam(BaseModel):
    name: str
    description: str
