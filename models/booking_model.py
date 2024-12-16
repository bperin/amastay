from typing import Optional, List
import uuid
from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from models.property_model import Property


class Booking(BaseModel, table=True):
    """Model representing a booking in the system"""

    __tablename__ = "bookings"

    notes: Optional[str] = Field(default=None)
    check_in: str = Field(max_length=50)
    check_out: str = Field(max_length=50)

    property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id")

    # Relationship attributes
    property: Optional[Property] = Relationship(back_populates="bookings")
    guests: List["BookingGuest"] = Relationship(back_populates="booking")
    messages: List["Message"] = Relationship(back_populates="booking")
