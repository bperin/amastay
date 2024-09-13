# import unittest
# from unittest.mock import patch, MagicMock
# from utils import supabase  # Import supabase from utils
# import uuid  # For generating UUIDs

# # Function to create a property
# def create_property(property_data):
#     """
#     Inserts a property into the Supabase database.
#     """
#     # Make sure owner_id is included in property_data
#     if 'owner_id' not in property_data:
#         property_data['owner_id'] = str(uuid.uuid4())  # Simulate an owner_id if none is provided
#     response = supabase.from_('properties').insert(property_data).execute()
#     return response


# class TestCreateProperty(unittest.TestCase):

#     @patch('utils.supabase')  # Mock the Supabase client from utils
#     def test_create_property(self, mock_supabase_client):
#         """
#         Test if a property is created successfully in the Supabase database.
#         """
#         # Generate a mock UUID for the property
#         mock_property_id = str(uuid.uuid4())
#         mock_owner_id = str(uuid.uuid4())  # Simulate a mock owner ID

#         # Mock property data with a generated UUID and mock owner_id
#         mock_property_data = {
#             'id': mock_property_id,
#             'name': 'Test Property',
#             'address': '123 Test Street',
#             'description': 'A beautiful test property.',
#             'owner_id': mock_owner_id  # Add the owner_id field explicitly
#         }

#         # Mock the Supabase response
#         mock_response = MagicMock()
#         mock_response.data = [{**mock_property_data}]
#         mock_response.error = None  # No error

#         # Mock the chain of calls for .from_().insert().execute()
#         mock_supabase_client.from_.return_value.insert.return_value.execute.return_value = mock_response

#         # Call the function to create the property
#         response = create_property(mock_property_data)

#         # Assert that the response has no error
#         self.assertIsNotNone(response.data)  # Ensure data is returned
#         self.assertGreater(len(response.data), 0)  # Ensure there's at least one record

#         # Compare only the relevant fields
#         for key in mock_property_data:
#             self.assertEqual(response.data[0][key], mock_property_data[key])

# if __name__ == "__main__":
#     unittest.main()
