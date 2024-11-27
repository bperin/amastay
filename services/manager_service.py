from typing import List, Optional
from uuid import UUID
from datetime import datetime

from models.manager import Manager
from supabase_utils import supabase_client, supabase_admin_client


class ManagerService:
    @staticmethod
    def create_manager(payload: dict) -> bool:
        """Create a new manager"""

        result = supabase_admin_client.auth.admin.invite_user_by_email(email=payload["email"], data=payload)

        if not result.data:
            raise ValueError("Failed to invite manager")

        return True

    @staticmethod
    def get_manager(id: str) -> Optional[Manager]:
        """Get a manager by ID"""
        result = supabase_client.from_("managers").select("*").eq("id", id).execute()
        return Manager(**result.data[0]) if result.data else None

    @staticmethod
    def get_managers_by_owner(owner_id: str) -> List[Manager]:
        """Get all managers for an owner"""
        result = supabase_client.from_("managers").select("*").eq("owner_id", owner_id).execute()
        return [Manager(**manager) for manager in result.data]

    @staticmethod
    def update_manager(payload: dict) -> Optional[Manager]:
        """Update a manager's information"""
        update_data = {}
        manager_id = payload.get("id")
        # Get existing manager data
        existing_manager = ManagerService.get_manager(str(manager_id))
        if not existing_manager:
            return None

        # TODO: Add validation for email and phone formats
        fields_to_check = ["first_name", "last_name", "email", "phone"]
        for field in fields_to_check:
            if field in payload and payload[field] != getattr(existing_manager, field):
                if field == "email":
                    update_data[field] = payload[field].lower()
                else:
                    update_data[field] = payload[field]

        if not update_data:
            return None

        result = supabase_client.table("managers").update(update_data).eq("id", str(manager_id)).execute()
        return Manager(**result.data[0]) if result.data else None

    @staticmethod
    def delete_manager(manager_id: UUID) -> bool:
        """Delete a manager"""
        # Get manager to verify ownership
        manager = ManagerService.get_manager(str(manager_id))
        if not manager:
            raise ValueError("Manager not found")
        if manager.owner_id != g.user_id:
            raise ValueError("You do not have permission to delete this manager")
        result = supabase_client.from_("managers").delete().eq("id", str(manager_id)).execute()
        return bool(result.data)
