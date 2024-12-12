from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID
from services.property_service import PropertyService
from services.property_information_service import PropertyInformationService
from auth_utils import get_current_user, require_owner, require_manager, require_owner_or_manager
from models.property import Property
from models.property_information import PropertyInformation
from geopy.geocoders import Nominatim
import logging

# Create router
router = APIRouter(prefix="/properties", tags=["properties"])

# Initialize the geolocator
geolocator = Nominatim(user_agent="amastay_property_geocoder")


class CreatePropertyInput(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    property_url: HttpUrl


class UpdatePropertyInput(BaseModel):
    id: UUID
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    property_url: Optional[HttpUrl] = None


class PropertyInfoInput(BaseModel):
    property_id: UUID
    name: str
    detail: str
    is_recommendation: bool
    metadata_url: Optional[HttpUrl] = None
    category_id: Optional[UUID] = None


class UpdatePropertyInfoInput(BaseModel):
    id: UUID
    name: Optional[str] = None
    detail: Optional[str] = None
    is_recommendation: Optional[bool] = None


@router.post("/create", response_model=Property, status_code=201)
async def create_property(data: CreatePropertyInput, current_user: dict = Depends(require_owner)):
    """Creates a new property (owners only)"""
    try:
        property_data = data.dict()

        # Clean property URL by removing query parameters
        if property_data["property_url"]:
            property_data["property_url"] = str(property_data["property_url"]).split("?")[0]

        # Create property with named parameters
        new_property = PropertyService.create_property(**property_data)
        return new_property
    except ValueError as ve:
        logging.error(f"Validation error in create_property: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in create_property: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.patch("/update", response_model=Property)
async def update_property(data: UpdatePropertyInput, current_user: dict = Depends(require_manager)):
    """Updates a property (managers only)"""
    try:
        updated_property = PropertyService.update_property(data.id, data.dict(exclude_unset=True))
        return updated_property
    except Exception as e:
        logging.error(f"Error in update_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_id}")
async def delete_property(property_id: UUID, current_user: dict = Depends(get_current_user)):
    """Deletes a property"""
    try:
        success = PropertyService.delete_property(str(property_id), current_user["id"])
        if success:
            return {"message": "Property deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete property")
    except Exception as e:
        logging.error(f"Error in delete_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[Property])
async def list_properties(current_user: dict = Depends(require_owner_or_manager)):
    """Lists all properties for the current user"""
    try:
        properties = PropertyService.list_properties(current_user["id"])
        return properties
    except Exception as e:
        logging.error(f"Error in list_properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/information", response_model=PropertyInformation)
async def add_property_information(data: PropertyInfoInput, current_user: dict = Depends(get_current_user)):
    """Adds information to a property"""
    try:
        property_info = PropertyInformationService.add_property_information(data.dict())
        return property_info
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error in add_property_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/information/{property_id}", response_model=List[PropertyInformation])
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


@router.patch("/information/update", response_model=PropertyInformation)
async def update_property_information(data: UpdatePropertyInfoInput, current_user: dict = Depends(get_current_user)):
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


@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: UUID, current_user: dict = Depends(get_current_user)):
    """Gets a specific property"""
    try:
        property = PropertyService.get_property(str(property_id))
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        return property
    except Exception as e:
        logging.error(f"Error in get_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))
