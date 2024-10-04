# app/controllers/booking_controller.py

from flask import Blueprint, request, jsonify
from services.booking_service import BookingService
from auth_utils import jwt_required

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/bookings", methods=["POST"])
@jwt_required
def create_booking():
    data = request.get_json()
    try:
        new_booking = BookingService.create_booking(data)
        return jsonify(new_booking.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@booking_bp.route("/bookings", methods=["GET"])
@jwt_required
def get_all_bookings():
    bookings = BookingService.get_all_bookings()
    return jsonify([booking.to_dict() for booking in bookings]), 200


@booking_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@jwt_required
def get_booking(booking_id):
    booking = BookingService.get_booking(booking_id)
    return jsonify(booking.to_dict()), 200


@booking_bp.route("/bookings/<int:booking_id>", methods=["PUT"])
@jwt_required
def update_booking(booking_id):
    data = request.get_json()
    updated_booking = BookingService.update_booking(booking_id, data)
    return jsonify(updated_booking.to_dict()), 200


@booking_bp.route("/bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required
def delete_booking(booking_id):
    BookingService.delete_booking(booking_id)
    return jsonify({"message": "Booking deleted successfully"}), 200


@booking_bp.route("/bookings/<int:booking_id>/guests", methods=["POST"])
@jwt_required
def add_booking_guest(booking_id):
    data = request.get_json()
    new_guest = BookingService.add_booking_guest(booking_id, data)
    return jsonify(new_guest.to_dict()), 201


@booking_bp.route("/bookings/guests/<int:guest_id>", methods=["DELETE"])
@jwt_required
def remove_booking_guest(guest_id):
    BookingService.remove_booking_guest(guest_id)
    return jsonify({"message": "Guest removed successfully"}), 200
