from typing import Optional
import uuid

import ormar

from models.base_model import BaseModel
from models.owner_model import Owner
from models.manager_model import Manager


class Property(BaseModel):

    class Meta(BaseModel.Meta):
        tablename = "properties"

    name: str = ormar.String(max_length=100)
    description: str = ormar.Text(nullable=True)
    address: str = ormar.String(max_length=200)
    lat: float = ormar.Float()
    lng: float = ormar.Float()
    property_url: str = ormar.String(max_length=200)

    # owner: Optional[Owner] = ormar.ForeignKey(Owner, nullable=False)
    # manager: Optional[Manager] = ormar.ForeignKey(Manager, nullable=True)
