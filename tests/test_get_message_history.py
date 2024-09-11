# tests/test_get_message_history.py
import unittest
from unittest.mock import patch, MagicMock
from get_message_history import get_message_history

class TestGetMessageHistory(unittest.TestCase):

    @patch('get_message_history.supabase')  # Mock the supabase client
    def test_get_recent_message_history(self, mock_supabase):
        # Mocking message retrieval response
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {'message_content': 'Hi, when is check-in?', 'sender_type': 'renter'},
            {'message_content': 'Check-in is at 3 PM.', 'sender_type': 'owner'}
        ]

        # Call the function to get recent message history
        result = get_message_history(1, limit=2)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['message_content'], 'Hi, when is check-in?')

if __name__ == "__main__":
    unittest.main()
