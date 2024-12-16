from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base_model import BaseModel


class Manager(BaseModel, table=True):
    """Manager model representing property managers"""

    __tablename__ = "managers"

    first_name: str = Field(max_length=100)
    last_name: Optional[str] = Field(max_length=100)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=20)
    verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)

    # Relationship attributes
    properties: List["Property"] = Relationship(back_populates="manager")
