# models/property_information.py

from typing import Optional
import uuid
from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from models.property_model import Property


class PropertyInformation(BaseModel, table=True):
    """Model representing property information details"""

    __tablename__ = "property_information"

    name: str = Field(max_length=255)
    detail: str = Field()  # SQLModel will use Text type for str without max_length
    is_recommendation: bool = Field(default=False)
    metadata_url: str = Field(max_length=255)
    category: str = Field(max_length=100)

    property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id")

    # Relationship attributes
    property: Optional[Property] = Relationship(back_populates="information")
