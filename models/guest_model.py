from typing import Optional, List
from sqlmodel import Field, Relationship
from models.base_model import BaseModel


class Guest(BaseModel, table=True):
    """Model representing a guest in the system"""

    __tablename__ = "guests"

    phone: str = Field(max_length=20)
    first_name: Optional[str] = Field(max_length=100, default=None)
    last_name: Optional[str] = Field(max_length=100, default=None)

    # Relationship attributes
    bookings: List["BookingGuest"] = Relationship(back_populates="guest")
