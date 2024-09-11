# tests/test_log_message.py
import unittest
from unittest.mock import patch, MagicMock
from log_message import log_message

class TestLogMessage(unittest.TestCase):

    @patch('log_message.supabase')  # Mock the supabase client
    def test_log_message(self, mock_supabase):
        # Mocking message logging response
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{'id': '1', 'message_content': 'Hi, what time is check-in?', 'sender_type': 'renter'}]

        # Call the function to log a message
        result = log_message(1, 'renter-uuid-1234', 'Hi, what time is check-in?', 'renter')

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['message_content'], 'Hi, what time is check-in?')

if __name__ == "__main__":
    unittest.main()
