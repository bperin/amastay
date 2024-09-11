# tests/test_create_booking.py
import unittest
from unittest.mock import patch, MagicMock
from create_booking import create_booking

class TestCreateBooking(unittest.TestCase):

    @patch('create_booking.supabase')  # Mock the supabase client
    def test_create_new_booking(self, mock_supabase):
        """
        Test creating a new booking with a renter UUID, property ID, and dates.
        """
        # Simulating the response when a new booking is created (with a generated UUID)
        mock_booking_data = {'id': 'generated-booking-uuid', 'status': 'active'}
        
        # Mock the insert response for booking creation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_booking_data]

        # Call the function to create a new booking (passing in mock UUIDs for renter and property)
        result = create_booking('renter-uuid-5678', 'property-uuid-1234', '2024-12-20', '2024-12-25')

        # Assertions to verify the booking creation result
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'active')
        self.assertEqual(result['id'], 'generated-booking-uuid')

if __name__ == "__main__":
    unittest.main()
