import ormar
from typing import Optional
from db_config import base_ormar_config
from models.owner import Owner


class Manager(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="managers")

    id: ormar.UUID = ormar.UUID(primary_key=True)

    first_name: str = ormar.String(max_length=100, nullable=True)
    last_name: Optional[str] = ormar.String(max_length=100, nullable=True)
    email: str = ormar.String(max_length=255, nullable=False)
    phone: Optional[str] = ormar.String(max_length=20, nullable=False)
    verified: bool = ormar.Boolean(default=False)
    phone_verified: bool = ormar.Boolean(default=False)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    owner: Optional[Owner] = ormar.ForeignKey(Owner, nullable=True)
