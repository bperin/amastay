from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

# Group model imports together
from models.manager_model import Manager, ManagerInvite, UpdateManager
from models.team_model import Team
from models.property_model import Property

# Group service imports together
from services.manager_service import ManagerService
from services.team_service import TeamService
from services.property_service import PropertyService
from models import *
from auth_utils import get_current_user
import logging


router = APIRouter(tags=["managers"])


@router.post("/invite", operation_id="invite_manager")
async def invite_manager(data: ManagerInvite, current_user: dict = Depends(get_current_user)):
    """Send invitation to a new manager"""
    try:
        result = ManagerService.create_manager_invitation(data, current_user["id"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error inviting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=List[Manager], operation_id="list_managers")
async def list_managers(current_user: dict = Depends(get_current_user)):
    """List all managers for the owner"""
    try:
        managers = ManagerService.get_managers_by_owner(current_user["id"])
        return managers
    except Exception as e:
        logging.error(f"Error listing managers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list_pending", response_model=List[Manager], operation_id="list_pending_managers")
async def list_pending_managers(current_user: dict = Depends(get_current_user)):
    """List all pending managers for the owner"""
    try:
        managers = ManagerService.get_pending_managers_by_owner(current_user["id"])
        return managers
    except Exception as e:
        logging.error(f"Error listing managers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get/{manager_id}", response_model=Manager, operation_id="get_manager")
async def get_manager(manager_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific manager"""
    try:
        manager = ManagerService.get_manager(manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        return manager
    except Exception as e:
        logging.error(f"Error getting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/update", response_model=Manager, operation_id="update_manager")
async def update_manager(data: UpdateManager, current_user: dict = Depends(get_current_user)):
    """Update a manager"""
    try:
        manager = ManagerService.update_manager(data)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        return manager
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error updating manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete/{manager_id}", operation_id="delete_manager")
async def delete_manager(manager_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a manager"""
    try:
        if ManagerService.delete_manager(maanger_id):
            return {"message": "Manager deleted successfully"}
        raise HTTPException(status_code=404, detail="Manager not found")
    except Exception as e:
        logging.error(f"Error deleting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
