import phonenumbers


class PhoneUtils:
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to E.164 format without + prefix"""
        try:
            parsed = phonenumbers.parse(phone, "US")
            return str(parsed.country_code) + str(parsed.national_number)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")
