from flask_restx import fields


def get_booking_input_models(ns_booking):
    """Define input models for booking endpoints"""

    booking_model = ns_booking.model(
        "Booking",
        {
            "property_id": fields.String(required=True, description="The property ID"),
            "check_in": fields.Integer(required=True, description="Check-in date and time as Unix timestamp"),
            "check_out": fields.Integer(required=True, description="Check-out date and time as Unix timestamp"),
            "status": fields.String(required=False, description="Booking status"),
        },
    )

    return {"booking_model": booking_model}
