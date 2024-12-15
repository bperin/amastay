import ormar
from typing import Optional
from db_config import base_ormar_config


class Owner(ormar.Model):
    class Meta:
        tablename = "owners"
        metadata = base_ormar_config.metadata
        database = base_ormar_config.database

    id: ormar.UUID = ormar.UUID(primary_key=True)
    phone: str = ormar.String(max_length=20)
    bio: Optional[str] = ormar.Text(nullable=True)

    first_name: str = ormar.String(max_length=100)
    last_name: str = ormar.String(max_length=100)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)
