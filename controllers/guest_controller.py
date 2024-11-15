import logging
import os
from typing import List
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from uuid import UUID

from services.booking_service import BookingService
from services.guest_service import GuestService
from services.pinpoint_service import PinpointService
from auth_utils import jwt_required

# Create namespace for guest-related routes
ns_guest = Namespace("guests", description="Guest management")

# Define model for guest operations
guest_model = ns_guest.model(
    "Guest",
    {
        "phone": fields.String(required=True, description="Guest's phone number"),
        "booking_id": fields.String(required=True, description="Booking id"),
        "first_name": fields.String(required=True, description="Guest's first name"),
        "last_name": fields.String(required=False, description="Guest's last name"),
    },
)


@ns_guest.route("/add")
class AddGuest(Resource):
    @ns_guest.doc("add_guest")
    @ns_guest.expect(guest_model)
    @jwt_required
    def post(self):
        """
        Adds a guest to a booking
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing guest data"}, 400

            phone_number = data.get("phone")
            booking_id = data.get("booking_id")
            first_name = data.get("first_name")
            last_name = data.get("last_name")

            guest = GuestService.get_or_create_guest(
                phone_number,
                first_name,
                last_name=last_name,
            )

            booking = BookingService.get_booking_by_id(booking_id)
            if not booking:
                return {"error": "Booking not found"}, 404

            booking_guest = BookingService.add_guest(guest.id, booking.id)

            if booking_guest:
                # Send welcome message to new guest
                try:
                    content = f"AmastayAI: You've been added to a reservation. " f"Reply YES to opt-in for updates about your stay. " f"Msg frequency varies. Msg & data rates may apply. " f"Text HELP for support, STOP to opt-out. " f"Booking ID: {booking_id}, Guest: {first_name} {last_name or ''}"
                    PinpointService.send_sms(phone_number, os.getenv("SYSTEM_PHONE_NUMBER"), content)
                except Exception as sms_error:
                    logging.error(f"Error sending welcome SMS: {sms_error}")

                return booking_guest.model_dump(), 200
            else:
                return {"error": "Failed to add guest"}, 400
        except Exception as e:
            logging.error(f"Error in add_guest: {e}")
            return {"error": str(e)}, 500


@ns_guest.route("/remove/<uuid:booking_id>/<uuid:guest_id>")
class RemoveGuest(Resource):
    @ns_guest.doc("remove_guest")
    @jwt_required
    def delete(self, booking_id: UUID, guest_id: UUID):
        """
        Removes a guest from a booking
        """
        try:
            success = GuestService.remove_guest(booking_id, guest_id)
            if success:
                return {"message": "Guest removed successfully"}, 200
            return {"error": "Failed to remove guest"}, 400
        except Exception as e:
            logging.error(f"Error in remove_guest: {e}")
            return {"error": str(e)}, 500


@ns_guest.route("/list/<uuid:booking_id>")
class ListGuests(Resource):
    @ns_guest.doc("list_guests")
    @jwt_required
    def get(self, booking_id: UUID):
        """
        Lists all guests for a booking
        """
        try:
            guests = GuestService.get_guests_by_booking(booking_id)
            return [guest.model_dump() for guest in guests], 200
        except Exception as e:
            logging.error(f"Error in list_guests: {e}")
            return {"error": str(e)}, 500
