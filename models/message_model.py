import ormar
from typing import Optional, TYPE_CHECKING
from db_config import base_ormar_config
from models.base_model import BaseModel
from models.booking_model import Booking
from models.guest_model import Guest


class Message(ormar.Model):

    class Meta(BaseModel.Meta):
        tablename = "messages"

    content: str = ormar.Text()  # Using Text for potentially longer messages
    sender_type: int = ormar.Integer()  # 0 for guest, 1 for AI, 2 for owner

    sms_id: Optional[str] = ormar.String(max_length=100, nullable=True)
    question_id: Optional[ormar.UUID] = ormar.UUID(nullable=True)

    # booking: Optional[Booking] = ormar.ForeignKey(Booking)
    # sender: Optional[Guest] = ormar.ForeignKey(Guest, nullable=True)
