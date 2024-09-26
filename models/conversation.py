# models/conversation.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Conversation(BaseModel):
    id: UUID
    booking_id: Optional[UUID]
    sender_type: Optional[str]  # 'owner' or 'renter'
    sender_id: Optional[UUID]
    message: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
