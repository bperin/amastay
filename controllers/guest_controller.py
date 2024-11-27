from flask_restx import Namespace, Resource, fields
from flask import request
from services.guest_service import GuestService
from services.booking_service import BookingService
from services.pinpoint_service import PinpointService
from auth_utils import jwt_required
import logging
import os
from uuid import UUID

# Create namespace
ns_guest = Namespace("guests", description="Guest management operations")

# Define request/response models
create_guest_model = ns_guest.model(
    "CreateGuest",
    {
        "phone": fields.String(required=True, description="Guest's phone number"),
        "booking_id": fields.String(required=True, description="Booking ID"),
        "first_name": fields.String(required=True, description="Guest's first name"),
        "last_name": fields.String(required=False, description="Guest's last name"),
    },
)

guest_response_model = ns_guest.model(
    "GuestResponse",
    {
        "id": fields.String(description="Guest ID"),
        "phone": fields.String(description="Phone number"),
        "email": fields.String(description="Email address"),
        "first_name": fields.String(description="First name"),
        "last_name": fields.String(description="Last name"),
        "created_at": fields.DateTime(description="Creation timestamp"),
        "updated_at": fields.DateTime(description="Last update timestamp"),
    },
)


@ns_guest.route("")
class GuestList(Resource):
    @ns_guest.doc("add_guest")
    @ns_guest.expect(create_guest_model)
    @ns_guest.response(200, "Success", guest_response_model)
    @jwt_required
    def post(self):
        """Add a guest to a booking"""
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing guest data"}, 400

            # Create or get guest
            guest = GuestService.get_or_create_guest(data)

            # Verify booking exists
            booking = BookingService.get_booking_by_id(data["booking_id"])
            if not booking:
                return {"error": "Booking not found"}, 404

            # Add guest to booking
            booking_guest = BookingService.add_guest(guest.id, booking.id)

            if booking_guest:
                # Send welcome message
                try:
                    content = f"AmastayAI: You've been added to a reservation. " f"Reply YES to opt-in for updates about your stay. " f"Msg frequency varies. Msg & data rates may apply. " f"Text HELP for support, STOP to opt-out. " f"Booking ID: {data['booking_id']}, " f"Guest: {data['first_name']} {data.get('last_name', '')}"
                    PinpointService.send_sms(data["phone"], os.getenv("SYSTEM_PHONE_NUMBER"), content)
                except Exception as sms_error:
                    logging.error(f"Error sending welcome SMS: {sms_error}")

                return guest.model_dump(), 200
            else:
                return {"error": "Failed to add guest"}, 400

        except Exception as e:
            logging.error(f"Error in add_guest: {e}")
            return {"error": str(e)}, 500


@ns_guest.route("/<uuid:booking_id>/<uuid:guest_id>")
class GuestDetail(Resource):
    @ns_guest.doc("remove_guest")
    @ns_guest.response(200, "Guest removed successfully")
    @jwt_required
    def delete(self, booking_id: UUID, guest_id: UUID):
        """Remove a guest from a booking"""
        try:
            data = {"booking_id": str(booking_id), "guest_id": str(guest_id)}
            success = GuestService.remove_guest(data)
            if success:
                return {"message": "Guest removed successfully"}, 200
            return {"error": "Failed to remove guest"}, 400

        except Exception as e:
            logging.error(f"Error in remove_guest: {e}")
            return {"error": str(e)}, 500


@ns_guest.route("/<uuid:booking_id>")
class BookingGuests(Resource):
    @ns_guest.doc("list_guests")
    @ns_guest.response(200, "Success", [guest_response_model])
    @jwt_required
    def get(self, booking_id: UUID):
        """List all guests for a booking"""
        try:
            guests = GuestService.get_guests_by_booking(str(booking_id))
            return {"guests": [guest.model_dump() for guest in guests]}, 200

        except Exception as e:
            logging.error(f"Error in list_guests: {e}")
            return {"error": str(e)}, 500
