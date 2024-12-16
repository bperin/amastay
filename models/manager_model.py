import ormar
from typing import Optional
from db_config import base_ormar_config
from models.base_model import BaseModel
from models.owner_model import Owner


class Manager(ormar.Model):

    class Meta(BaseModel.Meta):
        tablename = "managers"

    first_name: str = ormar.String(max_length=100, nullable=True)
    last_name: Optional[str] = ormar.String(max_length=100, nullable=True)
    email: str = ormar.String(max_length=255, nullable=False)
    phone: Optional[str] = ormar.String(max_length=20, nullable=False)
    verified: bool = ormar.Boolean(default=False)
    phone_verified: bool = ormar.Boolean(default=False)

    # owner: Optional[Owner] = ormar.ForeignKey(Owner, nullable=True)
