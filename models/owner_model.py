# models/owner_model.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base_model import BaseModel


class Owner(BaseModel, table=True):
    """Owner model representing property owners"""

    __tablename__ = "owners"

    phone: str = Field(max_length=20)
    bio: Optional[str] = Field(default=None)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)

    # Relationship attributes
    properties: List["Property"] = Relationship(back_populates="owner")
