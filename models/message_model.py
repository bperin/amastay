from typing import Optional
import uuid
from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from models.booking_model import Booking
from models.guest_model import Guest


class Message(BaseModel, table=True):
    """Model representing messages in the system"""

    __tablename__ = "messages"

    content: str = Field()  # SQLModel will use Text type for str without max_length
    sender_type: int = Field()  # 0 for guest, 1 for AI, 2 for owner
    sms_id: Optional[str] = Field(max_length=100, default=None)
    question_id: Optional[uuid.UUID] = Field(default=None)

    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")
    sender_id: Optional[uuid.UUID] = Field(default=None, foreign_key="guests.id")

    # Relationship attributes
    booking: Optional[Booking] = Relationship(back_populates="messages")
    sender: Optional[Guest] = Relationship(back_populates="sent_messages")
