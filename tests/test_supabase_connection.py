import unittest
import os
from amastay.supabase_utils import supabase_client, SUPABASE_URL


class TestSupabaseConnection(unittest.TestCase):
    def test_connection(self):
        """Test that we can connect to Supabase"""
        self.assertIsNotNone(SUPABASE_URL)
        self.assertIsNotNone(supabase_client)

        # Test connection by checking if client is initialized
        try:
            self.assertTrue(supabase_client.auth is not None)
        except Exception as e:
            self.fail(f"Failed to connect to Supabase: {str(e)}")

    def test_environment(self):
        """Test that required environment variables are set"""
        self.assertIsNotNone(os.environ.get("SUPABASE_URL"))
        self.assertIsNotNone(os.environ.get("SUPABASE_ANON_KEY"))
        self.assertIsNotNone(os.environ.get("SUPABASE_JWT_SECRET"))


if __name__ == "__main__":
    unittest.main()
