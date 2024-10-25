from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from models.booking import Booking
from models.guest import Guest
from models.booking_guest import BookingGuest
from services.guest_service import GuestService
from supabase_utils import supabase_client


class BookingService:

    @staticmethod
    def get_or_create_guest(phone_number: str, first_name: str, last_name: str) -> Guest:
        """
        Retrieves or creates a guest based on their phone number, first name, and last name.

        Args:
            phone_number (str): The phone number of the guest.
            first_name (str): The first name of the guest.
            last_name (str): The last name of the guest.

        Returns:
            Guest: A Guest object, either retrieved or newly created.
        """
        logging.info(f"Attempting to retrieve or create guest with phone number: {phone_number}")

        try:
            # Query the guests table by phone number
            guest_response = supabase_client.from_("guests").select("*").eq("phone", phone_number).execute()

            # If guest is found, return it
            if guest_response.data:
                logging.info(f"Guest found with phone number: {phone_number}")
                return Guest(**guest_response.data)

            logging.info(f"No guest found with phone number: {phone_number}. Creating a new guest.")

            # If no guest is found, create a new one
            new_guest_data = {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone_number,
            }
            new_guest_response = supabase_client.table("guests").insert(new_guest_data).execute()

            logging.info(f"New guest created with phone number: {phone_number}")

            # Return the newly created guest
            return Guest(**new_guest_response.data[0])

        except Exception as e:
            logging.error(f"Error in get_or_create_guest: {e}")
            raise

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
    def create_booking(booking_data: Dict[str, Any]) -> Booking:
        """
        Creates a new booking in the Supabase 'bookings' table.

        Args:
            booking_data (Dict[str, Any]): A dictionary containing the booking information.

        Returns:
            Booking: The created booking data returned by Supabase, cast to a Booking object.
        """
        try:
            # Parse check_in and check_out to timestamptz
            if "check_in" in booking_data:
                booking_data["check_in"] = datetime.fromtimestamp(booking_data["check_in"]).isoformat()
            if "check_out" in booking_data:
                booking_data["check_out"] = datetime.fromtimestamp(booking_data["check_out"]).isoformat()

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
        booking_id: str,
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
    ) -> Optional[BookingGuest]:
        """
        Adds a guest to a booking.

        Args:
            booking_id (str): The ID of the booking to add the guest to.
            phone_number (str): The phone number of the guest.
            first_name (str): The first name of the guest.
            last_name (Optional[str]): The last name of the guest (optional).
            greeting_message (Optional[str]): A greeting message for the guest (optional).

        Returns:
            Optional[BookingGuest]: The created BookingGuest object if successful, None otherwise.
        """
        try:
            # Get guest if not make it
            guest = BookingService.get_or_create_guest(phone_number, first_name, last_name)

            if not guest:
                raise ValueError("Failed to create or retrieve guest")

            # Add the guest to the booking
            booking_guest_data = {
                "booking_id": booking_id,
                "guest_id": guest.id,
            }
            booking_guest_response = supabase_client.table("booking_guests").insert(booking_guest_data).execute()

            if not booking_guest_response.data:
                raise ValueError("Failed to add guest to booking")

            # Create and return the BookingGuest object
            return BookingGuest(**booking_guest_response.data[0])

        except Exception as e:
            logging.error(f"Error adding guest to booking: {e}")
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
