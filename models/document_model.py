from typing import Optional
from pydantic import BaseModel, Field
from models import *


class Document(BaseModel):
    """Model representing document files in the system"""

    id: str = None
    file_id: str = None
    file_url: str = None
    primary: bool = False
    property_id: str = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    property_: Optional["Property"] = Field(default=None, alias="property")


class CreateDocument(BaseModel):
    file_id: str
    file_url: str
    primary: bool = False
    property_id: str


class UpdateDocument(BaseModel):
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    primary: Optional[bool] = None
