from typing import List, Optional
from datetime import datetime
from models.booking import Booking
from models.guest import Guest
from supabase_utils import supabase_client


class BookingService:

    @staticmethod
    def get_guest_by_phone(phone_number: str) -> Optional[Guest]:
        """
        Retrieves the guest information based on their phone number.

        Args:
            phone_number (str): The phone number of the guest.

        Returns:
            Optional[Guest]: A Guest object if found, None if no guest is found.
        """
        # Query the guests table by phone number
        guest_response = (
            supabase_client.table("guests")
            .select("*")  # Select all columns for the guest
            .eq("phone", phone_number)
            .single()
            .execute()
        )

        # If no guest data is found, return None
        if not guest_response.data:
            print(f"No guest found for phone number: {phone_number}")
            return None

        # Create and return a Guest object with the retrieved data
        return Guest(**guest_response.data)

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
        guest = BookingService.get_guest_by_phone(phone_number)

        # Step 2: Join 'booking_guests' and 'bookings' to get the next upcoming booking
        current_date = datetime.now().date()
        booking_response = (
            supabase_client.table("booking_guests")
            .select("bookings!inner(*)")  # Inner join with the 'bookings' table
            .eq("guest_id", guest.id)  # Filter by guest ID
            .gt("bookings.check_in", current_date)  # Only select future bookings
            .order(
                "bookings.check_in", ascending=True
            )  # Order by the nearest check-in date
            .limit(1)  # Get the next upcoming booking
            .single()
            .execute()
        )

        if not booking_response.data:
            print(f"No upcoming bookings found for guest ID: {guest.id}")
            return None

        # Step 3: Return the booking data as a Booking object
        return Booking(**booking_response.data["bookings"])
