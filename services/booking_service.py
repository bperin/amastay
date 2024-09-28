from supabase_utils import supabase_client
from datetime import datetime


class BookingService:

    @staticmethod
    def get_active_booking_by_phone(phone_number):
        """
        Get the active booking for a guest based on their phone number and the current date.
        Queries for a booking where the guest's phone number matches and the current date
        is within the check-in/check-out range.
        """
        current_date = datetime.now().date()

        # First, get the guest ID from the phone number
        guest_response = (
            supabase_client.table("guests")
            .select("id")
            .eq("phone", phone_number)
            .single()
            .execute()
        )

        if guest_response.data:
            guest_id = guest_response.data["id"]

            # Now, check for active bookings for this guest ID
            response = (
                supabase_client.table("bookings")
                .select("*")
                .eq("guest_id", guest_id)
                .lte("check_in", current_date)
                .gte("check_out", current_date)
                .execute()
            )

            if response.data:
                return response.data[0]  # Return the first active booking if found
        return None

    @staticmethod
    def get_booking_by_id(booking_id):
        """
        Fetch a specific booking by its ID.
        """
        response = (
            supabase_client.table("bookings")
            .select("*")
            .eq("id", booking_id)
            .single()
            .execute()
        )
        return response.data if response.data else None

    @staticmethod
    def get_conversation_participants(booking_id):
        """
        Retrieve all conversation participants based on a booking ID.
        This includes the guest and owner of the property for a specific booking.
        """
        response = (
            supabase_client.table("bookings")
            .select("guest_id, owner_id")
            .eq("id", booking_id)
            .single()
            .execute()
        )
        if response.data:
            guest_id = response.data["guest_id"]
            owner_id = response.data["owner_id"]

            # Fetch phone numbers for both guest and owner
            guest_response = (
                supabase_client.table("guests")
                .select("phone")
                .eq("id", guest_id)
                .single()
                .execute()
            )
            owner_response = (
                supabase_client.table("owners")
                .select("phone")
                .eq("id", owner_id)
                .single()
                .execute()
            )

            if guest_response.data and owner_response.data:
                participants = {
                    "guest_phone": guest_response.data["phone"],
                    "owner_phone": owner_response.data["phone"],
                }
                return participants
        return None
