import uuid
import ormar
from typing import Optional
from db_config import base_ormar_config
from models.base_model import BaseModel
from models.property_model import Property


class Booking(ormar.Model):
    class Meta(BaseModel.Meta):
        tablename = "bookings"

    notes: Optional[str] = ormar.Text(nullable=True)

    check_in: str = ormar.String(max_length=50)
    check_out: str = ormar.String(max_length=50)

    # property: Optional[Property] = ormar.ForeignKey(Property, nullable=True)
