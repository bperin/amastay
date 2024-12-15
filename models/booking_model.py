import ormar
from typing import Optional, TYPE_CHECKING
from db_config import base_ormar_config
from models.property_model import Property


class Booking(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="bookings")

    id: ormar.UUID = ormar.UUID(primary_key=True)
    notes: Optional[str] = ormar.Text(nullable=True)

    check_in: str = ormar.String(max_length=50)
    check_out: str = ormar.String(max_length=50)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    property: Optional[Property] = ormar.ForeignKey(Property, nullable=False)
