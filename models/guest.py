# models/renter.py

import ormar
from typing import Optional
from db_config import base_ormar_config
from pydantic import BaseModel


class Guest(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="guests")

    id: ormar.UUID = ormar.UUID(primary_key=True)
    phone: str = ormar.String(max_length=20)
    first_name: Optional[str] = ormar.String(max_length=100, nullable=True)
    last_name: Optional[str] = ormar.String(max_length=100, nullable=True)
    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)
