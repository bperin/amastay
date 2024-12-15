from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
from datetime import datetime


class Team(BaseModel):
    id: str
    name: str
    owner_id: str
    description: str
    created_at: str
    updated_at: str
