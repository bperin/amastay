# models/property_information.py

from pydantic import BaseModel
from typing import Optional

from models.property import Property


class PropertyInformation(BaseModel):
    id: str
    property_id: str
    name: str
    detail: str
    is_recommendation: bool
    metadata_url: str
    category: str
    created_at: str
    updated_at: str

    property: Optional[Property] = None
