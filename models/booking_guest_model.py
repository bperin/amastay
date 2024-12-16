from typing import Optional
import uuid
from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from models.booking_model import Booking
from models.guest_model import Guest


class BookingGuest(BaseModel, table=True):
    """Association model between bookings and guests"""

    __tablename__ = "booking_guests"

    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")
    guest_id: Optional[uuid.UUID] = Field(default=None, foreign_key="guests.id")

    # Relationship attributes
    booking: Optional[Booking] = Relationship(back_populates="guests")
    guest: Optional[Guest] = Relationship(back_populates="bookings")
