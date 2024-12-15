from typing import List, Optional
from datetime import datetime
import logging
from phone_utils import PhoneUtils
from models.manager_model import Manager
from supabase_utils import supabase_client, supabase_admin_client
from gotrue.types import InviteUserByEmailOptions


class ManagerService:

    @staticmethod
    def create_manager_invitation(first_name: str, last_name: str, phone: str, owner_id: str, email: str, team_id: Optional[str] = None) -> dict:
        """
        Creates an invitation for a manager to join a team.

        Args:
            owner_id: ID of the owner creating the invitation
            email: Email address of the invited manager
            team_id: ID of the team the manager is being invited to
        """
        try:
            phone = PhoneUtils.normalize_phone(phone)

            # Create the user account with manager role
            user_metadata = {"first_name": first_name, "last_name": last_name, "phone": phone, "user_type": "manager", "owner_id": owner_id}
            options = InviteUserByEmailOptions(data=user_metadata)
            response = supabase_admin_client.auth.admin.invite_user_by_email(email=email, options=options)

            if not response.user:
                raise ValueError("Failed to create manager account")

            # Create manager record in managers table
            manager_data = {"id": response.user.id, "owner_id": owner_id, "first_name": first_name, "last_name": last_name, "phone": phone, "email": email}

            result = supabase_client.from_("managers").insert(manager_data).execute()
            if not result.data:
                raise ValueError("Failed to create manager record")

            # Here you would typically send an email to the manager with their credentials
            # and a link to set up their account

            return {"message": "Manager invitation created successfully"}

        except Exception as e:
            logging.error(f"Error creating manager invitation: {e}")
            raise

    @staticmethod
    def get_manager(id: str) -> Optional[Manager]:
        """Get a manager by ID"""
        result = supabase_client.from_("managers").select("*").eq("id", id).execute()
        return Manager(**result.data[0]) if result.data else None

    @staticmethod
    def get_managers_by_owner(owner_id: str) -> List[Manager]:
        """Get all managers for an owner"""
        result = supabase_client.from_("managers").select("*").eq("owner_id", owner_id).execute()
        if not result.data:
            return []
        return [Manager(**manager) for manager in result.data]

    @staticmethod
    def get_pending_managers_by_owner(owner_id: str) -> List[Manager]:
        """Get all pending managers for an owner"""
        result = supabase_client.from_("managers").select("*").eq("owner_id", owner_id).execute()
        if not result.data:
            return []
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
    def delete_manager(manager_id: str) -> bool:
        """Delete a manager"""
        # Get manager to verify ownership
        manager = ManagerService.get_manager(str(manager_id))
        if not manager:
            raise ValueError("Manager not found")
        if manager.owner_id != g.user_id:
            raise ValueError("You do not have permission to delete this manager")
        result = supabase_client.from_("managers").delete().eq("id", str(manager_id)).execute()
        return bool(result.data)
