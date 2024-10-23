import logging
import os
from typing import List
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from models.booking import Booking
from services.booking_service import BookingService
from auth_utils import jwt_required
from uuid import UUID

from services.pinpoint_service import PinpointService

# Create the Namespace for booking-related routes
ns_booking = Namespace("bookings", description="Booking management")

# Define models for request/response
booking_model = ns_booking.model(
    "Booking",
    {
        "property_id": fields.String(required=True, description="The property ID"),
        "check_in": fields.Integer(
            required=True, description="Check-in date and time as Unix timestamp"
        ),
        "check_out": fields.Integer(
            required=True, description="Check-out date and time as Unix timestamp"
        ),
        "status": fields.String(required=False, description="Booking status"),
        # Add other fields as necessary
    },
)

# Define model for adding a guest
guest_model = ns_booking.model(
    "Guest",
    {
        "phone": fields.String(required=True, description="Guest's phone number"),
        "booking_id": fields.String(required=True, description="Booking id"),
        "first_name": fields.String(required=True, description="Guest's first name"),
        "last_name": fields.String(required=False, description="Guest's last name"),
        "greeting_message": fields.String(
            required=False, description="Optional greeting message"
        ),
    },
)


# Route to create a new booking
@ns_booking.route("/create")
class CreateBooking(Resource):
    @ns_booking.doc("create_booking")
    @ns_booking.expect(booking_model)
    @jwt_required
    def post(self):
        """
        Creates a new booking.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing booking data"}, 400

            new_booking = BookingService.create_booking(data)
            return new_booking.model_dump(), 201
        except ValueError as ve:
            logging.error(f"Validation error in create_booking: {ve}")
            return {"error": str(ve)}, 400
        except Exception as e:
            logging.error(f"Error in create_booking: {e}")
            return {"error": "An unexpected error occurred"}, 500


# Route to get all bookings
@ns_booking.route("/list")
class ListBookings(Resource):
    @ns_booking.doc("list_bookings")
    @jwt_required
    def get(self):
        """
        Lists all bookings.
        """
        try:
            bookings = BookingService.get_all_bookings()
            return [booking.model_dump() for booking in bookings], 200
        except Exception as e:
            logging.error(f"Error in list_bookings: {e}")
            return {"error": str(e)}, 500


# Route to get a specific booking by its ID
@ns_booking.route("/<uuid:booking_id>")
class ViewBooking(Resource):
    @ns_booking.doc("get_booking")
    @jwt_required
    def get(self, booking_id: UUID):
        """
        Retrieves a booking by its ID.
        """
        try:
            booking = BookingService.get_booking(booking_id)
            if not booking:
                return {"error": "Booking not found"}, 404
            return booking.model_dump(), 200
        except Exception as e:
            logging.error(f"Error in get_booking: {e}")
            return {"error": str(e)}, 500


# Route to update a booking
@ns_booking.route("/update/<uuid:booking_id>")
class UpdateBooking(Resource):
    @ns_booking.doc("update_booking")
    @ns_booking.expect(booking_model)
    @jwt_required
    def put(self, booking_id: UUID):
        """
        Updates a booking by its ID.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing update data"}, 400

            updated_booking = BookingService.update_booking(booking_id, data)
            return updated_booking.model_dump(), 200
        except Exception as e:
            logging.error(f"Error in update_booking: {e}")
            return {"error": str(e)}, 500


# Route to delete a booking
@ns_booking.route("/delete/<uuid:booking_id>")
class DeleteBooking(Resource):
    @ns_booking.doc("delete_booking")
    @jwt_required
    def delete(self, booking_id: UUID):
        """
        Deletes a booking by its ID.
        """
        try:
            success = BookingService.delete_booking(booking_id)
            if success:
                return {"message": "Booking deleted successfully"}, 200
            else:
                return {"error": "Failed to delete booking"}, 400
        except Exception as e:
            logging.error(f"Error in delete_booking: {e}")
            return {"error": str(e)}, 500


# Route to get bookings for a specific property
@ns_booking.route("/property/<uuid:property_id>")
class PropertyBookings(Resource):
    @ns_booking.doc("get_property_bookings")
    @jwt_required
    def get(self, property_id: UUID):
        """
        Retrieves all bookings for a specific property.
        """
        try:
            bookings = BookingService.get_bookings_by_property_id(property_id)
            return [booking.model_dump() for booking in bookings], 200
        except Exception as e:
            logging.error(f"Error in get_property_bookings: {e}")
            return {"error": str(e)}, 500


# Route to add a guest to a booking
@ns_booking.route("/add_guest")
class AddGuest(Resource):
    @ns_booking.doc("add_guest")
    @ns_booking.expect(guest_model)
    @jwt_required
    def post(self):
        """
        Adds a guest to a booking.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing guest data"}, 400

            phone_number = data.get("phone")
            booking_id = data.get("booking_id")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            greeting_message = data.get("greeting_message")

            if not phone_number or not first_name:
                return {"error": "Phone number and first name are required"}, 400

            updated_booking = BookingService.add_guest(
                booking_id,
                phone_number,
                first_name,
                last_name=last_name,
                greeting_message=greeting_message,
            )
            if updated_booking:
                # Send a welcome message to the new guest
                try:
                    content = greeting_message or f"Welcome to your stay, {first_name}!"
                    PinpointService.send_sms(
                        phone_number, os.getenv("SYSTEM_PHONE_NUMBER"), content
                    )
                except Exception as sms_error:
                    logging.error(f"Error sending welcome SMS: {sms_error}")
                    # Continue execution even if SMS fails

                return {
                    "message": "Guest added successfully",
                    "booking": updated_booking.model_dump(),
                }, 200
            else:
                return {"error": "Failed to add guest"}, 400
        except Exception as e:
            logging.error(f"Error in add_guest: {e}")
            return {"error": str(e)}, 500
