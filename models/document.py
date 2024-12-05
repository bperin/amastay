# models/document.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from models.property import Property


class Document(BaseModel):
    id: UUID
    property_id: UUID
    file_id: str
    file_url: str
    created_at: str
    updated_at: str

    property: Optional[Property] = None
