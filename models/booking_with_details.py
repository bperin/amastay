from typing import List, Optional
from pydantic import BaseModel
from models.booking import Booking
from models.guest import Guest
from models.property import Property


class BookingWithDetails(BaseModel):
    """
    A comprehensive model that combines a booking with its associated property and guests.
    """

    booking: Booking
    property: Property
    guests: List[Guest] = []
