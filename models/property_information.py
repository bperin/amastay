# models/property_information.py

from pydantic import BaseModel, Field
from typing import Optional


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
