from typing import Optional
from uuid import UUID
from models.booking_guest import BookingGuest
from models.guest import Guest
from supabase_utils import supabase_admin_client, supabase_client
import logging
import phonenumbers


class GuestService:

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to E.164 format without + prefix (e.g., 14155552671)"""
        try:
            # Parse number (defaults to US if no country code)
            parsed = phonenumbers.parse(phone, "US")
            # Format as E.164 and remove the + prefix
            return str(parsed.country_code) + str(parsed.national_number)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")

    @staticmethod
    def get_guest_by_phone(phone: str) -> Optional[Guest]:
        phone = GuestService.normalize_phone(phone)
        result = supabase_client.from_("guests").select("*").eq("phone", phone).limit(1).execute()
        return Guest(**result.data[0]) if result.data else None

    @staticmethod
    def get_or_create_guest(phone: str, first_name: str, last_name: str) -> Guest:
        phone = GuestService.normalize_phone(phone)
        guest = GuestService.get_guest_by_phone(phone)
        if not guest:
            response = supabase_admin_client.table("guests").insert({"phone": phone, "first_name": first_name, "last_name": last_name}).execute()
            guest = Guest(**response.data)  # Assuming create_guest returns inserted row
        return guest

    @staticmethod
    def update_guest(guest_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None):
        update_data = {}
        if first_name:
            update_data["first_name"] = first_name  # Update first name if provided
        if last_name:
            update_data["last_name"] = last_name  # Update last name if provided
        if phone:
            update_data["phone"] = phone  # Update phone if provided
        if email:
            update_data["email"] = email  # Update email if provided
        return supabase_admin_client.table("guests").update(update_data).eq("id", guest_id).execute()

    @staticmethod
    def delete_guest(guest_id: int):
        return supabase_admin_client.table("guests").delete().eq("id", guest_id).execute()

    @staticmethod
    def get_all_guests():
        return supabase_admin_client.table("guests").select("*").execute()

    @staticmethod
    def get_guests_by_booking(booking_id: UUID):
        result = supabase_client.table("booking_guests").select("guests!inner(*)").eq("booking_id", booking_id).execute()
        # Cast the result data to a list of Guest instances
        return [Guest(id=guest["guests"]["id"], email=guest["guests"]["email"], phone=guest["guests"]["phone"], last_name=guest["guests"]["last_name"], first_name=guest["guests"]["first_name"], created_at=guest["guests"]["created_at"], updated_at=guest["guests"]["updated_at"]) for guest in result.data] if result.data else []

    @staticmethod
    def get_booking_guests_by_booking(booking_id: UUID):
        result = supabase_client.table("booking_guests").select("*").eq("booking_id", booking_id).execute()
        # Cast the result data to a list of BookingGuest instances
        return [BookingGuest(id=guest["id"], booking_id=guest["booking_id"], guest_id=guest["guest_id"], created_at=guest["created_at"], updated_at=guest["updated_at"]) for guest in result.data] if result.data else []
