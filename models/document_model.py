from typing import Optional
import uuid
from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from models.property_model import Property


class Document(BaseModel, table=True):
    """Model representing document files in the system"""

    __tablename__ = "documents"

    file_id: str = Field(max_length=100)
    file_url: str = Field(max_length=255)
    primary: bool = Field(default=False)

    property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id")

    # Relationship attributes
    property: Optional[Property] = Relationship(back_populates="documents")
