import logging
import os
from typing import List
from flask import request, g
from flask_restx import Namespace, Resource, fields
from models.booking import Booking
from models.to_swagger import pydantic_to_swagger_model
from services.booking_service import BookingService
from auth_utils import jwt_required
from uuid import UUID
from .inputs.booking_inputs import get_booking_input_models
from models.booking_with_details import BookingWithDetails

# Create the Namespace for booking-related routes
ns_booking = Namespace("bookings", description="Booking management")

# Get input models
booking_input_models = get_booking_input_models(ns_booking)
create_booking_model = booking_input_models["booking_input_model"]
add_guest_model = booking_input_models["guest_input_model"]

booking_response_model = pydantic_to_swagger_model(ns_booking, "Booking", Booking)
booking_details_response_model = pydantic_to_swagger_model(ns_booking, "BookingDetailsResponse", BookingWithDetails)


# Route to create a new booking
@ns_booking.route("/create")
class CreateBooking(Resource):
    @ns_booking.doc("create_booking")
    @ns_booking.expect(create_booking_model)
    @ns_booking.response(201, "Success", booking_response_model)
    @jwt_required
    def post(self):
        """
        Creates a new booking.
        """
        try:
            data = request.get_json()

            if not data:
                return {"error": "Missing booking data"}, 400

            property_id = UUID(data.get("property_id"))
            check_in = data.get("check_in")
            check_out = data.get("check_out")
            notes = data.get("notes")

            if not property_id or not check_in or not check_out:
                return {"error": "Missing required booking fields"}, 400

            new_booking = BookingService.create_booking(property_id=property_id, check_in=check_in, check_out=check_out, notes=notes)
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
            # Check if bookings list is empty
            if not bookings:
                return [], 200
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
    @ns_booking.expect(booking_response_model)
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


@ns_booking.route("/details/<uuid:booking_id>")
class BookingDetails(Resource):
    @ns_booking.doc("get_booking_details")
    @jwt_required
    def get(self, booking_id: UUID):
        """
        Get a booking with its property and guest details.
        """
        try:
            booking_details = BookingService.get_booking_with_details(str(booking_id))
            if not booking_details:
                return {"error": "Booking not found"}, 404

            response = BookingDetailsResponse(booking=booking_details.booking, property=booking_details.property, guests=booking_details.guests)
            return response.model_dump(), 200

        except Exception as e:
            logging.error(f"Error in get_booking_details: {e}")
            return {"error": str(e)}, 500


@ns_booking.route("/details")
class BookingsDetails(Resource):
    @ns_booking.doc("get_bookings_details")
    @jwt_required
    def get(self):
        """
        Get all bookings with their property and guest details.
        Owner-specific results will be returned if owner_only=true query param is present.
        """
        try:
            owner_only = request.args.get("owner_only", "").lower() == "true"

            if owner_only:
                bookings = BookingService.get_bookings_by_owner_with_details()
            else:
                bookings = BookingService.get_all_bookings_with_details()

            response = BookingsDetailsResponse(bookings=[BookingDetailsResponse(booking=b.booking, property=b.property, guests=b.guests) for b in bookings])
            return response.model_dump(), 200

        except Exception as e:
            logging.error(f"Error in get_bookings_details: {e}")
            return {"error": str(e)}, 500


@ns_booking.route("/upcoming")
class UpcomingBooking(Resource):
    @ns_booking.doc("get_upcoming_booking")
    @jwt_required
    def get(self):
        """
        Get the next upcoming booking for a guest by their phone number.
        """
        try:
            phone = request.args.get("phone")
            if not phone:
                return {"error": "Phone number is required"}, 400

            booking = BookingService.get_next_upcoming_booking_by_phone(phone)
            if not booking:
                return {"error": "No upcoming bookings found"}, 404

            return {"booking": booking.model_dump()}, 200

        except Exception as e:
            logging.error(f"Error in get_upcoming_booking: {e}")
            return {"error": str(e)}, 500


@ns_booking.route("/guest/<uuid:guest_id>")
class GuestBooking(Resource):
    @ns_booking.doc("get_guest_booking")
    @jwt_required
    def get(self, guest_id: UUID):
        """
        Get the next booking for a specific guest by their ID.
        """
        try:
            booking = BookingService.get_next_booking_by_guest_id(str(guest_id))
            if not booking:
                return {"error": "No bookings found for this guest"}, 404

            return {"booking": booking.model_dump()}, 200

        except Exception as e:
            logging.error(f"Error in get_guest_booking: {e}")
            return {"error": str(e)}, 500
