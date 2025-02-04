import unittest
import uuid
from amastay.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def test_owner_sign_up(self):
        """Test property owner sign up"""
        test_email = f"owner_{uuid.uuid4()}@example.com"

        try:
            response = AuthService.sign_up_with_email_and_password(first_name="Test", last_name="Owner", email=test_email, password="OwnerTest123!", phone="+1234567890", user_type="owner")

            self.assertIsNotNone(response)
            self.assertIsNotNone(response.user)
            self.assertEqual(response.user.email, test_email)
            self.assertEqual(response.user.user_metadata["user_type"], "owner")

        except Exception as e:
            self.fail(f"Owner sign up failed: {str(e)}")


if __name__ == "__main__":
    unittest.main()
