from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from models.booking import Booking
from models.guest import Guest


class Message(BaseModel):
    id: str
    booking_id: str
    sender_id: Optional[str]
    sender_type: int  # 0 for guest, 1 for AI, 2 for owner
    content: str  # Message content
    sms_id: Optional[str]
    question_id: Optional[str]  # SMS message ID, optional if not an SMS message
    created_at: str
    updated_at: str

    booking: Optional[Booking] = None
    sender: Optional[Guest] = None
