from utils import supabase
from typing import Optional

def get_renter_info(booking_id: int) -> Optional[dict]:
    """Fetches renter information based on the booking ID."""
    response = supabase.table('bookings').select('renter_id, renter_name').eq('id', booking_id).execute()
    
    if response.data:
        renter = response.data[0]
        return {
            "id": renter['renter_id'],
            "name": renter['renter_name'],
            "role": "Renter"
        }
    
    return None

# Example usage
if __name__ == "__main__":
    booking_id = 1
    renter_info = get_renter_info(booking_id)
    print(f"Renter Info: {renter_info}")
