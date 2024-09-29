from supabase_utils import supabase_client
from datetime import datetime


class BookingService:

    @staticmethod
    def get_active_booking_by_sender_id(sender_id):
        """
        Get the active booking for a guest or owner based on their ID and the current date.
        Queries for a booking where the sender's ID matches and the current date
        is within the check-in/check-out range.
        """
        current_date = datetime.now().date()

        # Check for active bookings for this sender ID (guest or owner)
        response = (
            supabase_client.table("bookings")
            .select("*")
            .eq("guest_id", sender_id)  # Assuming the sender is a guest
            .or_("owner_id.eq." + sender_id)  # Or the sender is an owner
            .lte("check_in", current_date)
            .gte("check_out", current_date)
            .single()  # Fetch one active booking
            .execute()
        )

        if response.data:
            return response.data  # Return the active booking found
        return None
