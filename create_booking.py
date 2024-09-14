# create_booking.py
import supabase
from typing import Optional

def create_booking(renter_id: str, property_id: int, check_in_date: str, check_out_date: str) -> Optional[dict]:
    """Creates a booking entry for a renter."""
    new_booking_data = {
        'renter_id': renter_id,
        'property_id': property_id,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'status': 'active'
    }

    # Insert booking into the bookings table
    booking_response = supabase.table('bookings').insert(new_booking_data).execute()

    return booking_response.data[0] if booking_response.data else None

# Example usage
if __name__ == "__main__":
    renter_id = "renter-uuid-5678"
    property_id = 1  # Assuming property with ID 1 exists
    check_in_date = "2024-12-20"
    check_out_date = "2024-12-25"

    new_booking = create_booking(renter_id, property_id, check_in_date, check_out_date)
    print(f"Booking created: {new_booking}")
