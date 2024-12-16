from typing import Optional
from pydantic import BaseModel
from models.guest_model import Guest
from models.booking_model import Booking


class Message(BaseModel):
    """Model representing messages in the system"""

    id: str = None
    content: str = None
    sender_type: int = None  # 0 for guest, 1 for AI, 2 for owner
    sms_id: Optional[str] = None
    question_id: Optional[str] = None
    booking_id: str = None
    sender_id: Optional[str] = None
    created_at: str = None
    updated_at: str = None

    # Relationships
    booking: Optional["Booking"] = None
    sender: Optional["Guest"] = None


class CreateMessage(BaseModel):
    content: str
    sender_type: int
    booking_id: str
    sms_id: Optional[str] = None
    question_id: Optional[str] = None
    sender_id: Optional[str] = None


class UpdateMessage(BaseModel):
    content: Optional[str] = None
    sms_id: Optional[str] = None
    question_id: Optional[str] = None
