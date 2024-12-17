from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

# Group model imports together
from models.booking_model import Booking
from models.property_model import CreateProperty, Property, UpdateProperty
from models.document_model import Document
from models.property_information_model import PropertyInformation

# Group service imports together
from services.property_service import PropertyService
from services.booking_service import BookingService

from auth_utils import get_current_user
import logging

# Create router
router = APIRouter(tags=["properties"])


@router.post("/create", response_model=Property, status_code=201, operation_id="create_property")
async def create_property(create_property_input: CreateProperty, current_user: dict = Depends(get_current_user)):
    """Creates a new property (owners only)"""
    try:
        breakpoint()
        # Create property with named parameters
        new_property = await PropertyService.create_property(owner_id=current_user["id"], create_property_request=create_property_input)
        return new_property
    except ValueError as ve:
        breakpoint()
        logging.error(f"Validation error in create_property: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in create_property: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.patch("/update", response_model=Property, operation_id="update_property")
async def update_property(data: UpdateProperty, current_user: dict = Depends(get_current_user)):
    """Updates a property (managers only)"""
    try:
        updated_property = PropertyService.update_property(data.id, data.dict(exclude_unset=True))
        return updated_property
    except Exception as e:
        logging.error(f"Error in update_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/admin/update", response_model=Property, operation_id="admin_update_property")
async def admin_update_property(data: UpdateProperty, current_user: dict = Depends(get_current_user)):
    """Updates a property (managers only)"""
    try:
        updated_property = PropertyService.update_property(data.id, data.dict(exclude_unset=True))
        return updated_property
    except Exception as e:
        logging.error(f"Error in update_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_id}", operation_id="delete_property")
async def delete_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Deletes a property"""
    try:
        success = PropertyService.delete_property(property_id, current_user["id"])
        if success:
            return {"message": "Property deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete property")
    except Exception as e:
        logging.error(f"Error in delete_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_id}", operation_id="delete_property")
async def delete_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Deletes a property"""
    try:
        success = PropertyService.delete_property(property_id, current_user["id"])
        if success:
            return {"message": "Property deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete property")
    except Exception as e:
        logging.error(f"Error in delete_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[Property], operation_id="list_properties")
async def list_properties(current_user: dict = Depends(get_current_user)):
    """Lists all properties for the current user"""
    try:
        properties = PropertyService.list_properties(current_user["id"])
        return properties
    except Exception as e:
        logging.error(f"Error in list_properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{property_id}", response_model=Property, operation_id="get_property")
async def get_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Gets a specific property"""
    try:
        property = PropertyService.get_property(property_id)
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        return property
    except Exception as e:
        logging.error(f"Error in get_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{property_id}/bookings", response_model=List[Booking], operation_id="get_bookings_for_property")
async def get_property_bookings(property_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieves all bookings for a specific property"""
    try:
        bookings = BookingService.get_bookings_by_property_id(property_id)
        return bookings
    except Exception as e:
        logging.error(f"Error in get_property_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
