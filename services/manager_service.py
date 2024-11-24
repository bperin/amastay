from typing import List, Optional
from uuid import UUID
from datetime import datetime
from models.manager import Manager
from supabase_utils import supabase_client, supabase_admin_client


class ManagerService:
    @staticmethod
    def create_manager(owner_id: str, property_id: str, first_name: str, last_name: str, email: str, phone: Optional[str] = None) -> Manager:
        manager_data = {"owner_id": owner_id, "property_id": property_id, "first_name": first_name, "last_name": last_name, "email": email, "phone": phone}

        result = supabase_client.table("managers").insert(manager_data).execute()
        return Manager(**result.data[0])

    @staticmethod
    def get_manager(manager_id: str) -> Optional[Manager]:
        result = supabase_client.from_("managers").select("*").eq("id", str(manager_id)).execute()
        return Manager(**result.data[0]) if result.data else None

    @staticmethod
    def get_managers_by_property(property_id: str) -> List[Manager]:
        result = supabase_client.from_("managers").select("*").eq("property_id", str(property_id)).execute()
        return [Manager(**manager) for manager in result.data]

    @staticmethod
    def get_managers_by_owner(owner_id: str) -> List[Manager]:
        result = supabase_client.from_("managers").select("*").eq("owner_id", str(owner_id)).execute()
        return [Manager(**manager) for manager in result.data]

    @staticmethod
    def update_manager(manager_id: UUID, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Optional[Manager]:
        update_data = {}
        if first_name:
            update_data["first_name"] = first_name
        if last_name:
            update_data["last_name"] = last_name
        if email:
            update_data["email"] = email
        if phone:
            update_data["phone"] = phone

        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            result = supabase_client.table("managers").update(update_data).eq("id", str(manager_id)).execute()
            return Manager(**result.data[0]) if result.data else None
        return None

    @staticmethod
    def delete_manager(manager_id: UUID) -> bool:
        result = supabase_client.from_("managers").delete().eq("id", str(manager_id)).execute()
        return len(result.data) > 0
