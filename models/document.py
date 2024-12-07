# models/document.py

from pydantic import BaseModel
from typing import Optional

from models.property import Property


class Document(BaseModel):
    id: str
    property_id: str
    file_id: str
    file_url: str
    primary: bool
    created_at: str
    updated_at: str

    property: Optional[Property] = None
