# models/document.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class Document(BaseModel):
    id: str
    property_id: str
    file_id: str
    file_url: str
    created_at: str
    updated_at: str
