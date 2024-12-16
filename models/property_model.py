from typing import Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship
from .base_model import BaseModel


class Property(BaseModel, table=True):
    """Property model representing real estate properties"""

    __tablename__ = "properties"

    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    address: str = Field(max_length=200)
    lat: float
    lng: float
    property_url: str = Field(max_length=200)

    # Relationships will be defined here
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="owners.id")
    manager_id: Optional[uuid.UUID] = Field(default=None, foreign_key="managers.id")

    # Relationship attributes
    owner: Optional["Owner"] = Relationship(back_populates="properties")
    manager: Optional["Manager"] = Relationship(back_populates="properties")
