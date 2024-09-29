from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Message(BaseModel):
    id: UUID
    booking_id: UUID
    sender_id: UUID
    sender_type: int  # 0 for guest, 1 for AI, 2 for owner
    content: str  # Message content
    sms_id: Optional[str]  # SMS message ID, optional if not an SMS message
    created_at: datetime
    updated_at: datetime
