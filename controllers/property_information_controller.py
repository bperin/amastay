from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

# Group model imports together
from models.booking_model import Booking
from models.property_model import Property
from models.document_model import Document
from models.property_information_model import CreatePropertyInformation, PropertyInformation, UpdatePropertyInformation

# Group service imports together
from services.property_service import PropertyService
from services.property_information_service import PropertyInformationService
from services.booking_service import BookingService

from auth_utils import get_current_user
import logging

# Create router
router = APIRouter(tags=["property information"])


@router.post("/create", response_model=PropertyInformation, operation_id="create_property_information")
async def add_property_information(data: CreatePropertyInformation, current_user: dict = Depends(get_current_user)):
    """Adds information to a property"""
    try:
        property_info = PropertyInformationService.add_property_information(data.dict())
        return property_info
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in add_property_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{property_id}", response_model=List[PropertyInformation], operation_id="get_property_information")
async def get_property_information(property_id: UUID, current_user: dict = Depends(get_current_user)):
    """Gets all information for a property"""
    try:
        property_info = PropertyInformationService.get_property_information(str(property_id))
        if property_info is None:
            raise HTTPException(status_code=404, detail="Property information not found")
        return property_info
    except Exception as e:
        logging.error(f"Error in get_property_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update", response_model=PropertyInformation, operation_id="update_property_information")
async def update_property_information(data: UpdatePropertyInformation, current_user: dict = Depends(get_current_user)):
    """Updates property information"""
    try:
        updated_info = PropertyInformationService.update_property_information(data.dict(exclude_unset=True))
        if not updated_info:
            raise HTTPException(status_code=400, detail="Failed to update property information")
        return updated_info
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in update_property_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_info_id}", operation_id="delete_property_information")
async def delete_property_information(property_info_id: UUID, current_user: dict = Depends(get_current_user)):
    """Deletes property information"""
    try:
        success = PropertyInformationService.delete_property_information(str(property_info_id))
        if success:
            return {"message": "Property information deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete property information")
    except Exception as e:
        logging.error(f"Error in delete_property_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))
