# Standard library
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

# Models
from models.booking_model import Booking, CreateBooking, UpdateBooking, Guest
from models.guest_model import Guest
from models.booking_guest_model import BookingGuest
from models.property_model import Property

# Services
from services.guest_service import GuestService
from services.pinpoint_service import PinpointService
from services.property_service import PropertyService

# Utils
from phone_utils import PhoneUtils
from supabase_utils import supabase_client


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
    def create_booking(booking_data: CreateBooking) -> Optional[Booking]:
        """
        Creates a new booking with associated guests.

        Args:
            booking_data: CreateBooking model containing booking and guest information

        Returns:
            Optional[Booking]: The created booking with guests if successful
        """
        try:
            # Create the booking
            booking_dict = booking_data.model_dump(exclude={"guests"})
            booking_response = supabase_client.table("bookings").insert(booking_dict).execute()

            if not booking_response.data:
                raise Exception("Failed to create booking")

            booking_id = booking_response.data[0]["id"]

            # Then create the guests
            guests_data = [{"booking_id": booking_id, **guest.model_dump()} for guest in booking_data.guests]

            guests_response = supabase_client.table("booking_guests").insert(guests_data).execute()

            if not guests_response.data:
                # Rollback booking creation if guest creation fails
                supabase_client.table("bookings").delete().eq("id", booking_id).execute()
                raise Exception("Failed to create guests")

            # Get the complete booking with guests
            return BookingService.get_booking_by_id(booking_id)

        except Exception as e:
            logging.error(f"Error in create_booking: {e}")
            raise e

    @staticmethod
    def get_all_bookings() -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*,properties!inner(*)").execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving all bookings: {e}")
            raise

    @staticmethod
    def get_all_bookings_by_owner(owner_id: str) -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("properties.owner_id", owner_id).execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving all bookings: {e}")
            raise

    @staticmethod
    def get_all_bookings_by_property_id(property_id: str) -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").eq("property_id", property_id).execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving all bookings: {e}")
            raise

    @staticmethod
    def get_all_bookings_as_admin(admin_id: str) -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*, properties!inner(*)").execute()

            if not response.data:
                return []

            return [Booking(**booking_data) for booking_data in response.data]
        except Exception as e:
            print(f"Error retrieving all bookings: {e}")
            raise

    @staticmethod
    def get_all_bookings_by_manager(manager_id: str) -> List[Booking]:
        """
        Retrieves all bookings from the Supabase 'bookings' table.

        Returns:
            List[Booking]: A list of all bookings, each cast to a Booking object.
        """
        try:
            response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("properties.manager_id", manager_id).execute()

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
        try:
            response = (
                supabase_client.from_("bookings")
                .select(
                    """
                    *,
                    guests:booking_guests(*)
                """
                )
                .eq("id", booking_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            booking_data = response.data
            guests = [Guest(**guest) for guest in booking_data.pop("guests", [])]
            booking = Booking(**booking_data, guests=guests)

            return booking

        except Exception as e:
            logging.error(f"Error in get_booking_by_id: {e}")
            raise e

    # @staticmethod
    # def _build_booking_details(booking_data: Dict[str, Any]) -> BookingWithDetails:
    #     """
    #     Helper method to build a BookingWithDetails object from booking data.

    #     Args:
    #         booking_data (Dict[str, Any]): Raw booking data including properties

    #     Returns:
    #         BookingWithDetails: Constructed booking details object
    #     """
    #     # Create booking and property objects
    #     booking = Booking(**{k: v for k, v in booking_data.items() if k != "properties"})
    #     property_data = booking_data.get("properties")
    #     property_obj = Property(**property_data) if property_data else None

    #     # Get guests for this booking
    #     guests_response = supabase_client.table("booking_guests").select("guests(*)").eq("booking_id", booking.id).execute()

    #     guests = []
    #     if guests_response.data:
    #         guests = [Guest(**guest_data["guests"]) for guest_data in guests_response.data if guest_data.get("guests")]

    #     return BookingWithDetails(booking=booking, property=property_obj, guests=guests)

    @staticmethod
    def get_booking_with_details(user_id: str, booking_id: str) -> Optional[Booking]:
        """
        Retrieves a booking with its associated property and guest information.
        Verifies the user has access to the booking through property ownership or management.
        """
        try:
            booking_response = supabase_client.table("bookings").select("*, properties(*)").eq("id", booking_id).single().execute()

            if not booking_response.data:
                return None

            # Verify user has access through property ownership or management
            property_data = booking_response.data.get("properties")
            if property_data:
                user_id = str(user_id)
                if str(property_data.get("owner_id")) != user_id and str(property_data.get("manager_id")) != user_id:
                    return None

            return BookingService._build_booking_details(booking_response.data)

        except Exception as e:
            logging.error(f"Error retrieving booking details for booking ID {booking_id}: {e}")
            raise

    @staticmethod
    def get_all_bookings_with_details() -> List[Booking]:
        """
        Retrieves all bookings with their associated properties and guests.
        """
        try:
            bookings_response = supabase_client.table("bookings").select("*, properties(*)").execute()

            if not bookings_response.data:
                return []

            return [Booking(**booking_data) for booking_data in bookings_response.data]

        except Exception as e:
            logging.error(f"Error retrieving all bookings with details: {e}")
            raise

    @staticmethod
    def get_bookings_by_owner_with_details(owner_id: str) -> List[Booking]:
        """
        Retrieves all bookings with their associated properties and guests
        for properties owned by the current user.
        """
        try:
            bookings_response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("properties.owner_id", owner_id).execute()

            if not bookings_response.data:
                return []

            return [Booking(**booking_data) for booking_data in bookings_response.data]

        except Exception as e:
            logging.error(f"Error retrieving bookings for owner: {e}")
            raise

    @staticmethod
    def update_booking(*, booking_id: str, property_id: Optional[str] = None, check_in: Optional[int] = None, check_out: Optional[int] = None, notes: Optional[str] = None) -> Optional[Booking]:
        """
        Updates an existing booking in the Supabase 'bookings' table.

        Args:
            booking_id: UUID of the booking to update
            property_id: Optional UUID of the property
            check_in: Optional check-in timestamp in Unix epoch format
            check_out: Optional check-out timestamp in Unix epoch format
            notes: Optional booking notes

        Returns:
            Optional[Booking]: The updated booking if successful, None if booking not found
        """
        try:
            update_data = {}

            if property_id is not None:
                update_data["property_id"] = property_id
            if check_in is not None:
                update_data["check_in"] = datetime.fromtimestamp(check_in).isoformat()
            if check_out is not None:
                update_data["check_out"] = datetime.fromtimestamp(check_out).isoformat()
            if notes is not None:
                update_data["notes"] = notes

            response = supabase_client.table("bookings").update(update_data).eq("id", booking_id).execute()

            if not response.data:
                return None

            # Refetch booking with property details
            response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("id", booking_id).execute()
            if not response.data:
                return None

            return Booking(**response.data[0])
        except Exception as e:
            logging.error(f"Error updating booking {booking_id}: {e}")
            raise

    @staticmethod
    def get_booking_by_manager(user_id: str, booking_id: str) -> Optional[Booking]:
        """
        Retrieves a specific booking that belongs to properties managed by the manager.

        Args:
            booking_id (UUID): The ID of the booking to retrieve

        Returns:
            Optional[Booking]: The booking if found and managed by the manager, None otherwise
        """
        try:
            response = supabase_client.table("bookings").select("*, properties!inner(*)").eq("id", booking_id).single().execute()

            if not response.data:
                return None

            # Verify the property is managed by the manager
            property_data = response.data.get("properties")
            if not property_data or str(property_data.get("manager_id")) != str(user_id):
                return None

            return Booking(**response.data)
        except Exception as e:
            logging.error(f"Error retrieving booking {booking_id}: {e}")
            raise

    @staticmethod
    def delete_booking(user_id: str, booking_id: str) -> bool:
        """
        Deletes a booking from the database.

        Args:
            booking_id (UUID): The ID of the booking to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            booking = BookingService.get_booking_by_id(booking_id)
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} not found")

            property_id = booking.property_id
            property_obj = PropertyService.get_property(property_id)
            if not property_obj:
                raise ValueError(f"Property with ID {property_id} not found")

            if str(property_obj.owner_id) != str(user_id) and str(property_obj.manager_id) != str(user_id):
                raise ValueError(f"User does not have permission to delete booking for property {property_id}")

            # First delete associated booking_guests entries
            supabase_client.table("booking_guests").delete().eq("booking_id", booking_id).execute()

            # Then delete the booking
            response = supabase_client.table("bookings").delete().eq("id", booking_id).execute()

            return bool(response.data)
        except Exception as e:
            logging.error(f"Error deleting booking {booking_id}: {e}")
            return False
