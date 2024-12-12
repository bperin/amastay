# models/property.py
from typing import Optional


import ormar

from models.owner import Owner
from models.manager import Manager
from db_config import base_ormar_config


class Property(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="properties")

    id: ormar.UUID = ormar.UUID(primary_key=True)

    name: str = ormar.String(max_length=100)
    description: str = ormar.Text(nullable=True)
    address: str = ormar.String(max_length=200)
    lat: float = ormar.Float()
    lng: float = ormar.Float()

    property_url: str = ormar.String(max_length=200)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    owner: Optional[Owner] = ormar.ForeignKey(Owner, nullable=False)
    manager: Optional[Manager] = ormar.ForeignKey(Manager, nullable=True)
