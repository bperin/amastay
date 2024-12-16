# models/property_information.py

import ormar
from typing import Optional, TYPE_CHECKING
from db_config import base_ormar_config
from models.base_model import BaseModel
from models.property_model import Property


class PropertyInformation(ormar.Model):
    class Meta(BaseModel.Meta):
        tablename = "property_information"

    name: str = ormar.String(max_length=255)
    detail: str = ormar.Text()  # Using Text for potentially longer details
    is_recommendation: bool = ormar.Boolean(default=False)
    metadata_url: str = ormar.String(max_length=255)
    category: str = ormar.String(max_length=100)

    # property: Optional[Property] = ormar.ForeignKey(Property)
