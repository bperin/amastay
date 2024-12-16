# models/owner_model.py
import ormar
import uuid
from typing import Optional
from datetime import datetime
from .base_model import BaseModel


class Owner(BaseModel):
    class Meta(BaseModel.Meta):
        tablename = "owners"

    phone: str = ormar.String(max_length=20)
    bio: Optional[str] = ormar.Text(nullable=True)

    first_name: str = ormar.String(max_length=100)
    last_name: str = ormar.String(max_length=100)
