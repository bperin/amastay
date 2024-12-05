from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from models.booking import Booking
from models.guest import Guest
from models.booking_guest import BookingGuest
from services.guest_service import GuestService
from supabase_utils import supabase_client
from models.booking_with_details import BookingWithDetails
from models.property import Property
from flask import g


class BookingService:

    @staticmethod
    def get_next_upcoming_booking_by_phone(phone_number: str) -> Optional[Booking]:
        """
        Retrieves the next upcoming booking for a guest based on their phone number by joining
        the 'booking_guests' and 'bookings' tables.

        Args:
            phone_number (str): The phone number of the guest.

        Returns:
            Optional[Booking]: The next upcoming booking for the guest, or None if no booking is found.
        """
        # Step 1: Get the guest ID by phone number
        guest = GuestService.get_guest_by_phone(phone_number)

        # Step 2: Join 'booking_guests' and 'bookings' to get the next upcoming booking
        current_date = datetime.now().date()
        booking_response = supabase_client.table("booking_guests").select("bookings!inner(*)").eq("guest_id", guest.id).gt("bookings.check_in", current_date).order("bookings.check_in", ascending=True).limit(1).single().execute()  # Inner join with the 'bookings' table  # Filter by guest ID  # Only select future bookings  # Get the next upcoming booking

        if not booking_response.data:
            print(f"No upcoming bookings found for guest ID: {guest.id}")
            return None

        # Step 3: Return the booking data as a Booking object
        return Booking(**booking_response.data["bookings"])

    @staticmethod
    def create_booking(property_id: str, check_in: int, check_out: int, notes: Optional[str] = None) -> Booking:
        """
        Creates a new booking in the Supabase 'bookings' table.

        Args:
            property_id: ID of the property being booked
            check_in: Check-in timestamp in Unix epoch format
            check_out: Check-out timestamp in Unix epoch format
            notes: Optional booking notes

        Returns:
            Booking: The created booking data returned by Supabase, cast to a Booking object.
        """
        try:
            # Convert Unix timestamps to datetime objects
            check_in_dt = datetime.fromtimestamp(check_in)
            check_out_dt = datetime.fromtimestamp(check_out)
            booking_data = {"property_id": property_id, "check_in": check_in_dt.isoformat(), "check_out": check_out_dt.isoformat()}

            if notes:
                booking_data["notes"] = notes

            response = supabase_client.table("bookings").insert(booking_data).execute()

            if not response.data:
                raise ValueError("Failed to create booking")

            return Booking(**response.data[0])
        except Exception as e:
            print(f"Error creating booking: {e}")
            raise

    @staticmethod
    def get_all_bookings() -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*").execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving all bookings: {e}")
            raise

    @staticmethod
    def get_bookings_by_property_id(property_id: str) -> List[Booking]:
        """
        Retrieves all bookings for a specific property from the Supabase 'bookings' table.

        Args:
            property_id (str): The ID of the property to fetch bookings for.

        Returns:
            List[Booking]: A list of bookings for the specified property, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*").eq("property_id", property_id).execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving bookings for property {property_id}: {e}")
            raise

    @staticmethod
    def add_guest(
        guest_id: str,
        booking_id: str,
    ) -> Optional[BookingGuest]:
        """
        Adds a guest to a booking after verifying both exist.
        """
        try:
            # Verify booking exists
            booking_check = supabase_client.table("bookings").select("*").eq("id", booking_id).execute()
            if not booking_check.data:
                error_message = f"Booking with ID {booking_id} not found"
                logging.error(error_message)
                raise ValueError(error_message)

            # Verify guest exists
            guest_check = supabase_client.table("guests").select("*").eq("id", guest_id).execute()
            if not guest_check.data:  # Simplified check for guest existence
                error_message = f"Guest with ID {guest_id} not found"
                logging.error(error_message)
                raise ValueError(error_message)

            # Check if booking_guest already exists
            existing_guest_check = supabase_client.table("booking_guests").select("*").eq("booking_id", booking_id).eq("guest_id", guest_id).execute()
            if existing_guest_check.data:  # If a booking_guest exists
                # Return the existing BookingGuest instead of raising an error
                return BookingGuest(**existing_guest_check.data[0])  # Return existing guest

            # Add the guest to the booking
            booking_guest_data = {
                "booking_id": booking_id,
                "guest_id": guest_id,
            }
            booking_guest_response = supabase_client.table("booking_guests").insert(booking_guest_data).execute()

            if not booking_guest_response.data:
                raise ValueError("Failed to add guest to booking")

            return BookingGuest(**booking_guest_response.data[0])

        except Exception as e:
            logging.error(f"Error in add_guest: {e}")
            return None

    @staticmethod
    def get_next_booking_by_guest_id(guest_id: str) -> Optional[Booking]:
        """
        Retrieves the next upcoming booking for a guest based on their guest ID.

        Args:
            guest_id (str): The ID of the guest.

        Returns:
            Optional[Booking]: The next upcoming booking for the guest, or None if no booking is found.
        """
        try:
            current_date = datetime.now().date()
            booking_response = supabase_client.from_("booking_guests").select("bookings!inner(*)").eq("guest_id", guest_id).order("check_in", desc=False, foreign_table="bookings").limit(1).single().execute()

            if not booking_response.data:
                print(f"No upcoming bookings found for guest ID: {guest_id}")
                return None
            return Booking(**booking_response.data["bookings"])
        except Exception as e:
            print(f"Error retrieving next booking for guest ID {guest_id}: {e}")
            return None

    @staticmethod
    def get_booking_by_id(booking_id: str) -> Optional[Booking]:
        response = supabase_client.table("bookings").select("*").eq("id", booking_id).single().execute()
        return Booking(**response.data) if response.data else None

    @staticmethod
    def _build_booking_details(booking_data: Dict[str, Any]) -> BookingWithDetails:
        """
        Helper method to build a BookingWithDetails object from booking data.

        Args:
            booking_data (Dict[str, Any]): Raw booking data including properties

        Returns:
            BookingWithDetails: Constructed booking details object
        """
        # Create booking and property objects
        booking = Booking(**{k: v for k, v in booking_data.items() if k != "properties"})
        property_data = booking_data.get("properties")
        property_obj = Property(**property_data) if property_data else None

        # Get guests for this booking
        guests_response = supabase_client.table("booking_guests").select("guests(*)").eq("booking_id", booking.id).execute()

        guests = []
        if guests_response.data:
            guests = [Guest(**guest_data["guests"]) for guest_data in guests_response.data if guest_data.get("guests")]

        return BookingWithDetails(booking=booking, property=property_obj, guests=guests)

    @staticmethod
    def get_booking_with_details(booking_id: str) -> Optional[BookingWithDetails]:
        """
        Retrieves a booking with its associated property and guest information.
        """
        try:
            booking_response = supabase_client.table("bookings").select("*, properties(*)").eq("id", booking_id).single().execute()

            if not booking_response.data:
                return None

            return BookingService._build_booking_details(booking_response.data)

        except Exception as e:
            logging.error(f"Error retrieving booking details for booking ID {booking_id}: {e}")
            raise

    @staticmethod
    def get_all_bookings_with_details() -> List[BookingWithDetails]:
        """
        Retrieves all bookings with their associated properties and guests.
        """
        try:
            bookings_response = supabase_client.table("bookings").select("*, properties(*)").execute()

            if not bookings_response.data:
                return []

            return [BookingService._build_booking_details(booking_data) for booking_data in bookings_response.data]

        except Exception as e:
            logging.error(f"Error retrieving all bookings with details: {e}")
            raise

    @staticmethod
    def get_bookings_by_owner_with_details() -> List[BookingWithDetails]:
        """
        Retrieves all bookings with their associated properties and guests
        for properties owned by the current user.
        """
        try:
            bookings_response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("properties.owner_id", g.user_id).execute()

            if not bookings_response.data:
                return []

            return [BookingService._build_booking_details(booking_data) for booking_data in bookings_response.data]

        except Exception as e:
            logging.error(f"Error retrieving bookings for owner: {e}")
            raise
