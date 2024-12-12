# models/owner.py

import ormar
from pydantic import BaseModel
from typing import Optional
from db_config import base_ormar_config


class Owner(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="owners")

    id: ormar.UUID = ormar.UUID(primary_key=True)
    phone: str = ormar.String(max_length=20)
    bio: Optional[str] = ormar.Text(nullable=True)

    first_name: str = ormar.String(max_length=100)
    last_name: str = ormar.String(max_length=100)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)
