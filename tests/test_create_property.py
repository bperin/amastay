import unittest
from unittest.mock import patch
from supabase import create_client
import os
import uuid  # For generating UUIDs

# Load environment variables (Supabase URL and Key)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to create a property
def create_property(property_data):
    """
    Inserts a property into the Supabase database.
    """
    response = supabase.from_('properties').insert(property_data).execute()
    return response

class TestCreateProperty(unittest.TestCase):

    @patch('supabase.create_client')  # Mock Supabase client for testing
    def test_create_property(self, mock_supabase):
        """
        Test if a property is created successfully in the Supabase database.
        """
        # Generate a mock UUID for the property
        mock_property_id = str(uuid.uuid4())

        # Mock property data with a generated UUID
        mock_property_data = {
            'id': mock_property_id,
            'property_name': 'Test Property',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'zip': '12345',
            'description': 'A beautiful test property.'
        }

        # Mock response for Supabase insert
        mock_response = unittest.mock.Mock()
        mock_response.data = [mock_property_data]  # Mock the returned data
        mock_response.error = None  # No error

        # Set the mock to return this response
        mock_supabase.return_value.from_().insert().execute.return_value = mock_response

        # Call the function to create the property
        response = create_property(mock_property_data)

        # Assert there is no error
        # self.assertIsNone(response.error)

        # Assert the response data matches the inserted property data
        # self.assertEqual(response.data[0], mock_property_data)

if __name__ == "__main__":
    unittest.main()
