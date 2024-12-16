import uuid
import ormar
from typing import Optional
from models.base_model import BaseModel


class Guest(ormar.Model):
    class Meta(BaseModel.Meta):
        tablename = "guests"

    phone: str = ormar.String(max_length=20)
    first_name: Optional[str] = ormar.String(max_length=100, nullable=True)
    last_name: Optional[str] = ormar.String(max_length=100, nullable=True)
