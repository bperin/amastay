# First import models without relationships
from .property_model import Property, CreateProperty, UpdateProperty
from .owner_model import Owner, CreateOwner, UpdateOwner
from .manager_model import Manager, CreateManager, UpdateManager
from .booking_model import Booking, CreateBooking, UpdateBooking
from .guest_model import Guest, CreateGuest, UpdateGuest
from .booking_guest_model import BookingGuest, CreateBookingGuest, UpdateBookingGuest
from .message_model import Message, CreateMessage, UpdateMessage
from .document_model import Document, CreateDocument, UpdateDocument
from .property_information_model import PropertyInformation, CreatePropertyInformation, UpdatePropertyInformation

# Export all models
__all__ = [
    "Property",
    "CreateProperty",
    "UpdateProperty",
    "Owner",
    "CreateOwner",
    "UpdateOwner",
    "Manager",
    "CreateManager",
    "UpdateManager",
    "Booking",
    "CreateBooking",
    "UpdateBooking",
    "Guest",
    "CreateGuest",
    "UpdateGuest",
    "BookingGuest",
    "CreateBookingGuest",
    "UpdateBookingGuest",
    "Message",
    "CreateMessage",
    "UpdateMessage",
    "Document",
    "CreateDocument",
    "UpdateDocument",
    "PropertyInformation",
    "CreatePropertyInformation",
    "UpdatePropertyInformation",
]
