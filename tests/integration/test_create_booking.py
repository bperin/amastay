import unittest
from supabase import create_client
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class TestCreateBooking(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize test data
        """
        self.renter_data = {
            "email_address": "renter@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "0987654321",
            "user_role": "renter"
        }

    def test_create_booking(self):
        """
        Test the insertion of booking into the database
        """
        # Insert renter
        renter = supabase.from_('users').insert(self.renter_data).execute()
        self.assertEqual(renter.status_code, 201)

        renter_id = renter.data[0]['id']  # Grab the inserted renter's id
        property_id = supabase.from_('properties').select('id').eq('property_name', 'Airbnb Property Test').execute().data[0]['id']

        # Insert the booking
        booking_data = {
            "renter_id": renter_id,
            "property_id": property_id,
            "check_in_date": "2024-10-01",
            "check_out_date": "2024-10-05",
            "status": "confirmed"
        }
        booking = supabase.from_('bookings').insert(booking_data).execute()
        self.assertEqual(booking.status_code, 201)

if __name__ == '__main__':
    unittest.main()
