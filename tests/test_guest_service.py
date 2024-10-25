import unittest
from unittest.mock import patch, MagicMock
from services.guest_service import GuestService


class TestGuestService(unittest.TestCase):

    @patch("amastay.services.guest_service.SupabaseUtils.get_admin_client")
    def setUp(self, mock_get_admin_client):
        self.mock_supabase = MagicMock()
        mock_get_admin_client.return_value = self.mock_supabase

    def test_create_guest(self):
        mock_response = MagicMock()
        mock_response.data = {
            "id": 1,
            "phone": "+11234567890",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.mock_supabase.table().insert().execute.return_value = mock_response

        result = GuestService.create_guest("+11234567890", "John", "Doe")

        self.assertEqual(result.data, mock_response.data)
        self.mock_supabase.table.assert_called_once_with("guests")
        self.mock_supabase.table().insert.assert_called_once_with({"phone": "+11234567890", "first_name": "John", "last_name": "Doe"})

    def test_get_guest_by_phone(self):
        mock_response = MagicMock()
        mock_response.data = {
            "id": 1,
            "phone": "+11234567890",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.mock_supabase.table().select().eq().single().execute.return_value = mock_response

        result = GuestService.get_guest_by_phone("+11234567890")

        self.assertEqual(result.data, mock_response.data)
        self.mock_supabase.table.assert_called_once_with("guests")
        self.mock_supabase.table().select().eq.assert_called_once_with("phone", "+11234567890")

    def test_get_or_create_guest_existing(self):
        mock_response = MagicMock()
        mock_response.data = {
            "id": 1,
            "phone": "+11234567890",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.mock_supabase.table().select().eq().single().execute.return_value = mock_response

        result = GuestService.get_or_create_guest("+11234567890", "John", "Doe")

        self.assertEqual(result, mock_response.data)
        self.mock_supabase.table().insert.assert_not_called()

    def test_get_or_create_guest_new(self):
        self.mock_supabase.table().select().eq().single().execute.return_value = MagicMock(data=None)

        mock_create_response = MagicMock()
        mock_create_response.data = {
            "id": 1,
            "phone": "+11234567890",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.mock_supabase.table().insert().execute.return_value = mock_create_response

        result = GuestService.get_or_create_guest("+11234567890", "John", "Doe")

        self.assertEqual(result, mock_create_response.data)
        self.mock_supabase.table().insert.assert_called_once()

    def test_update_guest(self):
        mock_response = MagicMock()
        mock_response.data = {
            "id": 1,
            "name": "John Smith",
            "email": "john@example.com",
        }
        self.mock_supabase.table().update().eq().execute.return_value = mock_response

        result = GuestService.update_guest(1, name="John Smith", email="john@example.com")

        self.assertEqual(result.data, mock_response.data)
        self.mock_supabase.table.assert_called_once_with("guests")
        self.mock_supabase.table().update.assert_called_once_with({"name": "John Smith", "email": "john@example.com"})
        self.mock_supabase.table().update().eq.assert_called_once_with("id", 1)

    def test_delete_guest(self):
        mock_response = MagicMock()
        mock_response.data = {"id": 1}
        self.mock_supabase.table().delete().eq().execute.return_value = mock_response

        result = GuestService.delete_guest(1)

        self.assertEqual(result.data, mock_response.data)
        self.mock_supabase.table.assert_called_once_with("guests")
        self.mock_supabase.table().delete().eq.assert_called_once_with("id", 1)

    def test_get_all_guests(self):
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "phone": "+11234567890",
                "first_name": "John",
                "last_name": "Doe",
            },
            {
                "id": 2,
                "phone": "+10987654321",
                "first_name": "Jane",
                "last_name": "Smith",
            },
        ]
        self.mock_supabase.table().select().execute.return_value = mock_response

        result = GuestService.get_all_guests()

        self.assertEqual(result.data, mock_response.data)
        self.mock_supabase.table.assert_called_once_with("guests")
        self.mock_supabase.table().select.assert_called_once_with("*")


if __name__ == "__main__":
    unittest.main()
