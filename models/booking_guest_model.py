import ormar

from models.base_model import BaseModel
from models.booking_model import Booking
from models.guest_model import Guest


class BookingGuest(ormar.Model):
    class Meta(BaseModel.Meta):
        tablename = "booking_guests"

    # booking: Optional[Booking] = ormar.ForeignKey(Booking)
    # guest: Optional[Guest] = ormar.ForeignKey(Guest)
