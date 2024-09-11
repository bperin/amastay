# tests/test_create_conversation.py
import unittest
from unittest.mock import patch, MagicMock
from create_conversation import create_or_get_conversation
import uuid

class TestCreateConversation(unittest.TestCase):

    @patch('create_conversation.supabase')  # Mock the supabase client
    def test_create_new_conversation(self, mock_supabase):
        """
        Test creating a new conversation when no existing conversation is found.
        """
        # Mocking no existing conversation (empty data)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Simulating a new conversation creation response with UUIDs
        mock_conversation_data = {
            'id': str(uuid.uuid4()),  # Generated UUID for the conversation
            'booking_id': str(uuid.uuid4()),  # Mock UUID for booking
            'property_id': str(uuid.uuid4()),  # Mock UUID for property
            'status': 'active'
        }

        # Mocking the insert response for conversation creation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_conversation_data]

        # Call the function to create a new conversation (passing in mock UUIDs)
        result = create_or_get_conversation(mock_conversation_data['booking_id'], mock_conversation_data['property_id'])

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'active')
        self.assertEqual(result['id'], mock_conversation_data['id'])

    @patch('create_conversation.supabase')  # Mock the supabase client
    def test_get_existing_conversation(self, mock_supabase):
        """
        Test fetching an existing conversation when a conversation is found.
        """
        # Simulating an existing conversation in the database
        mock_existing_conversation = {
            'id': str(uuid.uuid4()),  # Generated UUID for the conversation
            'booking_id': str(uuid.uuid4()),  # Mock UUID for booking
            'property_id': str(uuid.uuid4()),  # Mock UUID for property
            'status': 'active'
        }

        # Mocking the select response for fetching an existing conversation
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_existing_conversation]

        # Call the function to fetch the existing conversation
        result = create_or_get_conversation(mock_existing_conversation['booking_id'], mock_existing_conversation['property_id'])

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'active')
        self.assertEqual(result['id'], mock_existing_conversation['id'])

if __name__ == "__main__":
    unittest.main()
