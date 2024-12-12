from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from services.team_service import TeamService
from auth_utils import get_current_user
from models.team import Team
from models.manager import Manager
import logging


router = APIRouter(prefix="/teams", tags=["teams"])


class CreateTeamInput(BaseModel):
    name: str
    description: str


class AssignTeamToPropertyInput(BaseModel):
    team_id: UUID
    property_id: UUID


class AssignManagerToTeamInput(BaseModel):
    team_id: UUID
    manager_id: UUID


@router.post("/create", response_model=Team)
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


@router.get("/list", response_model=List[Team])
async def list_teams(current_user: dict = Depends(get_current_user)):
    """Get all teams owned by the current user"""
    try:
        teams = TeamService.get_owner_teams(current_user["id"])
        return teams
    except Exception as e:
        logging.error(f"Error in get_owner_teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign_property")
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


@router.get("/{team_id}/managers", response_model=List[Manager])
async def get_team_managers(team_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get all managers of a team"""
    try:
        managers = TeamService.get_team_managers(str(team_id))
        return managers
    except Exception as e:
        logging.error(f"Error in get_team_managers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/properties", response_model=List[Manager])
async def get_team_properties(team_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get all properties of a team"""
    try:
        properties = TeamService.get_team_properties(str(team_id))
        return properties
    except Exception as e:
        logging.error(f"Error in get_team_properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign_manager")
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


@router.delete("/{team_id}/managers/{manager_id}")
async def remove_manager_from_team(team_id: UUID, manager_id: UUID, current_user: dict = Depends(get_current_user)):
    """Remove a manager from a team"""
    try:
        data = {"team_id": str(team_id), "manager_id": str(manager_id), "owner_id": current_user["id"]}
        result = TeamService.remove_manager_from_team(data)
        return result
    except Exception as e:
        logging.error(f"Error in remove_manager_from_team: {e}")
        raise HTTPException(status_code=500, detail=str(e))
