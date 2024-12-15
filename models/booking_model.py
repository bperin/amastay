import ormar
from typing import Optional
from db_config import base_ormar_config
from models.property_model import Property


class Booking(ormar.Model):
    class Meta:
        tablename = "bookings"
        metadata = base_ormar_config.metadata
        database = base_ormar_config.database

    id: ormar.UUID = ormar.UUID(primary_key=True)
    notes: Optional[str] = ormar.Text(nullable=True)

    check_in: str = ormar.String(max_length=50)
    check_out: str = ormar.String(max_length=50)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    property: Optional[Property] = ormar.ForeignKey(Property, nullable=True)
