# models/property_information.py

from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from models.property import Property


class PropertyInformation(BaseModel):
    id: UUID
    property_id: UUID
    name: str
    detail: str
    is_recommendation: bool
    metadata_url: str
    category: str
    created_at: str
    updated_at: str

    property: Optional[Property] = None
