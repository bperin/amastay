# models/property_information.py

import ormar
from typing import Optional
from db_config import base_ormar_config
from models.property import Property


class PropertyInformation(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="property_information")

    id: ormar.UUID = ormar.UUID(primary_key=True)
    name: str = ormar.String(max_length=255)
    detail: str = ormar.Text()  # Using Text for potentially longer details
    is_recommendation: bool = ormar.Boolean(default=False)
    metadata_url: str = ormar.String(max_length=255)
    category: str = ormar.String(max_length=100)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    property: Optional[Property] = ormar.ForeignKey(Property)
