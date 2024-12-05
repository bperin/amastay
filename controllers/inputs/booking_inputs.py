from flask_restx import fields


def get_booking_input_models(ns_booking):
    """Define input models for booking endpoints"""

    booking_input_model = ns_booking.model(
        "CreateBooking",
        {
            "property_id": fields.String(required=True, description="The property ID"),
            "check_in": fields.Integer(required=True, description="Check-in date and time as Unix timestamp"),
            "check_out": fields.Integer(required=True, description="Check-out date and time as Unix timestamp"),
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

    return {"booking_input_model": booking_input_model, "guest_input_model": guest_input_model}
