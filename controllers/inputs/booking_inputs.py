from flask_restx import fields


def get_booking_input_models(ns_booking):
    """Define input models for booking endpoints"""

    booking_input_model = ns_booking.model(
        "CreateBooking",
        {
            "property_id": fields.String(required=True, description="The property ID"),
            "notes": fields.String(required=False, description="Booking notes"),
            "check_in": fields.String(required=True, description="Check-in date and time as ISO timestamp"),
            "check_out": fields.String(required=True, description="Check-out date and time as ISO timestamp"),
        },
    )
    update_booking_model = ns_booking.model(
        "UpdateBooking",
        {
            "booking_id": fields.String(required=False, description="The booking ID"),
            "property_id": fields.String(required=False, description="The property ID"),
            "notes": fields.String(required=False, description="Booking notes"),
            "check_in": fields.Integer(required=False, description="Check-in date and time as Unix timestamp"),
            "check_out": fields.Integer(required=False, description="Check-out date and time as Unix timestamp"),
        },
    )
    guest_input_model = ns_booking.model(
        "AddGuest",
        {
            "booking_id": fields.String(required=True, description="The property ID"),
            "first_name": fields.String(required=True, description="First name"),
            "last_name": fields.String(required=True, description="Last name"),
            "phone": fields.String(required=True, description="Phone number"),
        },
    )

    return {"booking_input_model": booking_input_model, "guest_input_model": guest_input_model, "update_booking_model": update_booking_model}
