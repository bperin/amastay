from typing import Dict, List, Optional
import logging
from models.manager import Manager
from models.property import Property
from models.team import Team
from supabase_utils import supabase_client
from datetime import datetime
from pydantic import BaseModel


class TeamService:
    """Service for managing property management teams"""

    @staticmethod
    def create_team(data: Dict) -> Team:
        """
        Creates a new team for an owner.

        Args:
            data: Dictionary containing team data (name, owner_id, description)
        """
        try:
            result = supabase_client.table("teams").insert(data).execute()

            if not result.data:
                raise Exception("Failed to create team")

            return Team(**result.data[0])

        except Exception as e:
            logging.error(f"Error creating team: {e}")
            raise

    @staticmethod
    def get_owner_teams(owner_id: str) -> List[Team]:
        """Retrieves all teams owned by the specified owner"""
        try:
            result = supabase_client.from_("teams").select("*").eq("owner_id", owner_id).execute()

            return [Team(**team) for team in result.data]

        except Exception as e:
            logging.error(f"Error fetching owner teams: {e}")
            raise

    @staticmethod
    def assign_team_to_property(data: Dict) -> Dict:
        """
        Assigns a team to manage a property.

        Args:
            data: Dictionary containing team_id, property_id, and owner_id
        """
        try:
            team_id = data["team_id"]
            owner_id = data["owner_id"]
            property_id = data["property_id"]

            # Verify owner owns both the team and property
            team = supabase_client.from_("teams").select("*").eq("id", team_id).eq("owner_id", owner_id).single().execute()

            if not team.data:
                raise Exception("Team not found or not owned by this user")

            property_check = supabase_client.from_("properties").select("*").eq("id", property_id).eq("owner_id", owner_id).single().execute()

            if not property_check.data:
                raise Exception("Property not found or not owned by this user")

            # Create the assignment
            assignment_data = {"team_id": team_id, "property_id": property_id}

            result = supabase_client.table("property_teams").insert(assignment_data).execute()

            if not result.data:
                raise Exception("Failed to assign team to property")

            return {"message": "Team assigned to property successfully"}

        except Exception as e:
            logging.error(f"Error assigning team to property: {e}")
            raise

    @staticmethod
    def assign_manager_to_team(data: Dict):
        """
        Assigns a manager to a team
        """
        # Assigns a manager to a team
        # Args:
        #     data: Dictionary containing team_id, manager_id, and owner_id
        try:
            team_id = data["team_id"]
            manager_id = data["manager_id"]
            owner_id = data["owner_id"]

            # Verify owner owns the team
            team = supabase_client.table("teams").select("*").eq("id", team_id).eq("owner_id", owner_id).single().execute()

            if not team.data:
                raise Exception("Team not found or not owned by this user")

            # Create the assignment
            assignment_data = {"team_id": team_id, "manager_id": manager_id}

            result = supabase_client.table("manager_teams").insert(assignment_data).execute()

            if not result.data:
                raise Exception("Failed to assign manager to team")

            return {"message": "Manager assigned to team successfully"}

        except Exception as e:
            logging.error(f"Error assigning manager to team: {e}")
            raise

    @staticmethod
    def get_team_managers(team_id: str) -> List[Manager]:
        """
        Retrieves all managers for a team using inner join pattern

        Args:
            team_id: The ID of the team
        Returns:
            List of manager details
        """
        try:
            # Following the pattern from guest_service.py where it does:
            result = supabase_client.from_("manager_teams").select("managers!inner(*)").eq("team_id", team_id).execute()

            return [Manager(**manager["managers"]) for manager in result.data] if result.data else []

        except Exception as e:
            logging.error(f"Error fetching team managers: {e}")
            raise

    @staticmethod
    def get_team_properties(team_id: str) -> List[Property]:
        """
        Retrieves all properties for a team using inner join pattern

        Args:
            team_id: The ID of the team
        Returns:
            List of property details
        """
        try:
            # Following the pattern from guest_service.py where it does:
            result = supabase_client.from_("property_teams").select("properties!inner(*)").eq("team_id", team_id).execute()

            return [Property(**property["properties"]) for property in result.data] if result.data else []

        except Exception as e:
            logging.error(f"Error fetching team properties: {e}")
            raise

    @staticmethod
    def remove_manager_from_team(data: Dict):
        """
        Removes a manager from a team

        Args:
            data: Dictionary containing team_id, user_id, and owner_id
        """
        try:
            # Verify owner owns the team
            team = supabase_client.table("teams").select("*").eq("id", data["team_id"]).eq("owner_id", data["owner_id"]).single().execute()

            if not team.data:
                raise Exception("Team not found or not owned by this user")

            result = supabase_client.table("manager_teams").delete().eq("team_id", data["team_id"]).eq("manager_id", data["manager_id"]).execute()

            if not result.data:
                raise Exception("Failed to remove manager from team")

            return {"message": "Manager removed from team successfully"}

        except Exception as e:
            logging.error(f"Error removing team member: {e}")
            raise
