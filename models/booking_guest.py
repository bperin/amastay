# models/booking_guest.py
import ormar
from typing import Optional, TYPE_CHECKING
from db_config import base_ormar_config
from models.booking import Booking
from models.guest import Guest


class BookingGuest(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="booking_guests")

    id: ormar.UUID = ormar.UUID(primary_key=True)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    booking: Optional[Booking] = ormar.ForeignKey(Booking)
    guest: Optional[Guest] = ormar.ForeignKey(Guest)
