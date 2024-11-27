import pytest
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime


def get_supabase() -> Client:
    """Initialize Supabase client using environment variables"""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


@pytest.fixture
def supabase_client():
    """Fixture to provide Supabase client"""
    return get_supabase()


def test_happy_flow_supabase(supabase_client):
    """Test the complete happy flow using actual Supabase database"""

    # Create a test user via Supabase auth
    test_email = f"test_{datetime.now().timestamp()}@test.com"
    test_password = "test_password123!"

    # Sign up new test user
    auth_response = supabase_client.auth.sign_up({"email": test_email, "password": test_password})
    user_id = auth_response.user.id

    try:
        # Create managers
        manager1_data = {"email": f"manager1_{datetime.now().timestamp()}@test.com", "name": "Manager One", "created_by": user_id}
        manager1 = supabase_client.table("managers").insert(manager1_data).execute()
        manager1_id = manager1.data[0]["id"]

        manager2_data = {"email": f"manager2_{datetime.now().timestamp()}@test.com", "name": "Manager Two", "created_by": user_id}
        manager2 = supabase_client.table("managers").insert(manager2_data).execute()
        manager2_id = manager2.data[0]["id"]

        # Create teams
        team1_data = {"name": f"Team Alpha {datetime.now().timestamp()}", "created_by": user_id}
        team1 = supabase_client.table("teams").insert(team1_data).execute()
        team1_id = team1.data[0]["id"]

        team2_data = {"name": f"Team Beta {datetime.now().timestamp()}", "created_by": user_id}
        team2 = supabase_client.table("teams").insert(team2_data).execute()
        team2_id = team2.data[0]["id"]

        # Assign managers to teams
        manager_team1_data = {"manager_id": manager1_id, "team_id": team1_id, "assigned_by": user_id}
        supabase_client.table("manager_teams").insert(manager_team1_data).execute()

        manager_team2_data = {"manager_id": manager2_id, "team_id": team2_id, "assigned_by": user_id}
        supabase_client.table("manager_teams").insert(manager_team2_data).execute()

        # Create properties
        property1_data = {"name": f"Beach House {datetime.now().timestamp()}", "address": "123 Beach Road", "created_by": user_id}
        property1 = supabase_client.table("properties").insert(property1_data).execute()
        property1_id = property1.data[0]["id"]

        property2_data = {"name": f"Mountain Cabin {datetime.now().timestamp()}", "address": "456 Mountain Trail", "created_by": user_id}
        property2 = supabase_client.table("properties").insert(property2_data).execute()
        property2_id = property2.data[0]["id"]

        # Assign properties to teams
        property_team1_data = {"property_id": property1_id, "team_id": team1_id, "assigned_by": user_id}
        supabase_client.table("property_teams").insert(property_team1_data).execute()

        property_team2_data = {"property_id": property2_id, "team_id": team2_id, "assigned_by": user_id}
        supabase_client.table("property_teams").insert(property_team2_data).execute()

        # Test getters using Supabase queries
        # Verify managers in teams
        team1_managers = supabase_client.table("manager_teams").select("managers(*)").eq("team_id", team1_id).execute()
        assert len(team1_managers.data) == 1
        assert team1_managers.data[0]["managers"]["id"] == manager1_id

        # Verify properties in teams
        team1_properties = supabase_client.table("property_teams").select("properties(*)").eq("team_id", team1_id).execute()
        assert len(team1_properties.data) == 1
        assert team1_properties.data[0]["properties"]["id"] == property1_id

        # Verify manager's teams
        manager1_teams = supabase_client.table("manager_teams").select("teams(*)").eq("manager_id", manager1_id).execute()
        assert len(manager1_teams.data) == 1
        assert manager1_teams.data[0]["teams"]["id"] == team1_id

    finally:
        # Cleanup: Delete all created test data
        supabase_client.table("property_teams").delete().eq("property_id", property1_id).execute()
        supabase_client.table("property_teams").delete().eq("property_id", property2_id).execute()

        supabase_client.table("manager_teams").delete().eq("manager_id", manager1_id).execute()
        supabase_client.table("manager_teams").delete().eq("manager_id", manager2_id).execute()

        supabase_client.table("properties").delete().eq("id", property1_id).execute()
        supabase_client.table("properties").delete().eq("id", property2_id).execute()

        supabase_client.table("teams").delete().eq("id", team1_id).execute()
        supabase_client.table("teams").delete().eq("id", team2_id).execute()

        supabase_client.table("managers").delete().eq("id", manager1_id).execute()
        supabase_client.table("managers").delete().eq("id", manager2_id).execute()

        # Delete test user
        supabase_client.auth.admin.delete_user(user_id)
