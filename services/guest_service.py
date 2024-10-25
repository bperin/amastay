from typing import Optional
from models.guest import Guest
from supabase_utils import supabase_admin_client, supabase_client


class GuestService:
    @staticmethod
    def create_guest(phone: str, first_name: str, last_name: Optional[str] = None):
        return supabase_admin_client.table("guests").insert({"phone": phone, "first_name": first_name, "last_name": last_name}).execute()

    @staticmethod
    def get_guest_by_phone(phone: str) -> Optional[Guest]:
        # Strip the '+' from the beginning of the phone number if present
        phone = phone.lstrip("+")

        # Ensure the phone number starts with '1'
        if not phone.startswith("1"):
            phone = "1" + phone

        result = supabase_client.from_("guests").select("*").eq("phone", phone).single().execute()

        if result.data:
            return Guest(**result.data)
        return None

    @staticmethod
    def get_or_create_guest(phone: str, first_name: str, last_name: Optional[str] = None):
        # Normalize the phone number
        if not phone.startswith("+1"):
            phone = "+1" + phone.lstrip("1")  # Remove leading '1' if present, then add '+1'

        guest = GuestService.get_guest_by_phone(phone)
        if not guest.data:
            guest = GuestService.create_guest(phone, first_name, last_name)
        return guest.data

    @staticmethod
    def update_guest(guest_id: int, name: Optional[str] = None, email: Optional[str] = None):
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        return supabase_admin_client.table("guests").update(update_data).eq("id", guest_id).execute()

    @staticmethod
    def delete_guest(guest_id: int):
        return supabase_admin_client.table("guests").delete().eq("id", guest_id).execute()

    @staticmethod
    def get_all_guests():
        return supabase_admin_client.table("guests").select("*").execute()
