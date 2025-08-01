from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Group model imports together
from models.team_model import Team
from models.manager_model import Manager
from models.property_model import Property

# Group service imports together
from services.team_service import TeamService
from services.manager_service import ManagerService
from services.property_service import PropertyService

from auth_utils import get_current_user
import logging


router = APIRouter(tags=["teams"])


class CreateTeamInput(BaseModel):
    name: str
    description: str


class AssignTeamToPropertyInput(BaseModel):
    team_id: str
    property_id: str


class AssignManagerToTeamInput(BaseModel):
    team_id: str
    manager_id: str


@router.post("/create", response_model=Team, operation_id="create")
async def create_team(data: CreateTeamInput, current_user: dict = Depends(get_current_user)):
    """Create a new team"""
    try:
        team_data = data.dict()
        team_data["owner_id"] = current_user["id"]
        result = TeamService.create_team(team_data)
        return result
    except Exception as e:
        logging.error(f"Error in create_team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[Team], operation_id="list")
async def list_teams(current_user: dict = Depends(get_current_user)):
    """Get all teams owned by the current user"""
    try:
        teams = TeamService.get_owner_teams(current_user["id"])
        return teams
    except Exception as e:
        logging.error(f"Error in get_owner_teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign_property", operation_id="assign_property")
async def assign_team_to_property(data: AssignTeamToPropertyInput, current_user: dict = Depends(get_current_user)):
    """Assign a team to manage a property"""
    try:
        team_data = data.dict()
        team_data["owner_id"] = current_user["id"]
        result = TeamService.assign_team_to_property(team_data)
        return result
    except Exception as e:
        logging.error(f"Error in assign_team_to_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/managers", response_model=List[Manager], operation_id="get_team_managers")
async def get_team_managers(team_id: str, current_user: dict = Depends(get_current_user)):
    """Get all managers of a team"""
    try:
        managers = TeamService.get_team_managers(team_id)
        return managers
    except Exception as e:
        logging.error(f"Error in get_team_managers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/properties", response_model=List[Manager], operation_id="get_team_properties")
async def get_team_properties(team_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get all properties of a team"""
    try:
        properties = TeamService.get_team_properties(str(team_id))
        return properties
    except Exception as e:
        logging.error(f"Error in get_team_properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign_manager", operation_id="assign_manager")
async def assign_manager_to_team(data: AssignManagerToTeamInput, current_user: dict = Depends(get_current_user)):
    """Assign a manager to a team"""
    try:
        team_data = data.dict()
        team_data["owner_id"] = current_user["id"]
        result = TeamService.assign_manager_to_team(team_data)
        return result
    except Exception as e:
        logging.error(f"Error in assign_manager_to_team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}/managers/{manager_id}", operation_id="remove_manager")
async def remove_manager_from_team(team_id: str, manager_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a manager from a team"""
    try:
        data = {"team_id": team_id, "manager_id": manager_id, "owner_id": current_user["id"]}
        result = TeamService.remove_manager_from_team(data)
        return result
    except Exception as e:
        logging.error(f"Error in remove_manager_from_team: {e}")
        raise HTTPException(status_code=500, detail=str(e))
