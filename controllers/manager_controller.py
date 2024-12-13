from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID
from services.manager_service import ManagerService
from auth_utils import get_current_user
from models.manager import Manager
import logging


router = APIRouter(prefix="/managers", tags=["managers"])


class ManagerInviteInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    team_id: Optional[UUID] = None


class UpdateManagerInput(BaseModel):
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


@router.post("/invite", operation_id="invite")
async def invite_manager(data: ManagerInviteInput, current_user: dict = Depends(get_current_user)):
    """Send invitation to a new manager"""
    try:
        result = ManagerService.create_manager_invitation(first_name=data.first_name, last_name=data.last_name, phone=data.phone, owner_id=current_user["id"], email=str(data.email), team_id=str(data.team_id) if data.team_id else None)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error inviting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=List[Manager], operation_id="list")
async def list_managers(current_user: dict = Depends(get_current_user)):
    """List all managers for the owner"""
    try:
        managers = ManagerService.get_managers_by_owner(current_user["id"])
        return managers
    except Exception as e:
        logging.error(f"Error listing managers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list_pending", response_model=List[Manager], operation_id="list_pending")
async def list_pending_managers(current_user: dict = Depends(get_current_user)):
    """List all pending managers for the owner"""
    try:
        managers = ManagerService.get_pending_managers_by_owner(current_user["id"])
        return managers
    except Exception as e:
        logging.error(f"Error listing managers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{manager_id}", response_model=Manager, operation_id="get_manager")
async def get_manager(manager_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get a specific manager"""
    try:
        manager = ManagerService.get_manager(str(manager_id))
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        return manager
    except Exception as e:
        logging.error(f"Error getting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/update", response_model=Manager, operation_id="update")
async def update_manager(data: UpdateManagerInput, current_user: dict = Depends(get_current_user)):
    """Update a manager"""
    try:
        manager = ManagerService.update_manager(data.dict(exclude_unset=True))
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        return manager
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error updating manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{manager_id}", operation_id="delete")
async def delete_manager(manager_id: UUID, current_user: dict = Depends(get_current_user)):
    """Delete a manager"""
    try:
        if ManagerService.delete_manager(str(manager_id)):
            return {"message": "Manager deleted successfully"}
        raise HTTPException(status_code=404, detail="Manager not found")
    except Exception as e:
        logging.error(f"Error deleting manager: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
