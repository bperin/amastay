from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl

# Group model imports together
from models.booking_model import Booking
from models.property_model import CreateProperty, Property, UpdateProperty
from models.document_model import Document
from models.property_information_model import PropertyInformation
from models.property_metadata_model import ScrapeAsyncResponse

# Group service imports together
from models.property_photo_model import PropertyPhoto
from services.property_service import PropertyService
from services.booking_service import BookingService
from services.scraper_service import ScraperService

from auth_utils import get_current_user
import logging

from services.vertex_service import VertexService

# Create router
router = APIRouter(tags=["properties"])


@router.post("", response_model=Property, operation_id="create_property")
async def create_property(
    background_tasks: BackgroundTasks,
    property: CreateProperty,
    current_user: dict = Depends(get_current_user),
):
    """Create a new property."""
    try:
        # Create the property first
        new_property = PropertyService.create_property(property, current_user["id"])

        # Trigger async scraping
        background_tasks.add_task(PropertyService.scrape_and_index_property, property_id=new_property.id, user_id=current_user["id"])

        return new_property
    except Exception as e:
        logging.error(f"Failed to create property: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{property_id}/scrape", status_code=202, response_model=ScrapeAsyncResponse, operation_id="scrape_property")
async def scrape_property(property_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Initiates property scraping in the background"""
    try:
        property = PropertyService.get_property(property_id)
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")

        # Add scraping task to background tasks
        background_tasks.add_task(ScraperService.scrape_property_background, property)

        return ScrapeAsyncResponse(message="Property scraping initiated this may take a few minutes", property_id=property_id, status="processing")
    except Exception as e:
        logging.error(f"Error in scrape_property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update", response_model=Property, operation_id="update_property")
async def update_property(data: UpdateProperty, current_user: dict = Depends(get_current_user)):
    """Updates a property (managers only)"""
    try:
        updated_property = await PropertyService.update_property(data.id, data.dict(exclude_unset=True))
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


@router.delete("/delete/{property_id}", operation_id="delete_property")
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
        if not properties:
            return []
        return [property.model_dump() for property in properties]
    except Exception as e:
        logging.error(f"Error in list_properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{property_id}", response_model=Property, operation_id="get_property")
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


@router.get("/bookings/{property_id}", response_model=List[Booking], operation_id="get_bookings_for_property")
async def get_property_bookings(property_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieves all bookings for a specific property"""
    try:
        bookings = BookingService.get_bookings_by_property_id(property_id)
        if len(bookings) == 0:
            return []
        return [booking.model_dump() for booking in bookings]
    except Exception as e:
        logging.error(f"Error in get_property_bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/details/{property_id}", response_model=Property, operation_id="get_property_details")
async def get_property_details(property_id: str, current_user: dict = Depends(get_current_user)):
    """
    Gets property details including owner and manager information
    """
    try:
        property = PropertyService.get_property_details(property_id)
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        return property.model_dump()
    except Exception as e:
        logging.error(f"Error in get_property_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/photos/{property_id}", response_model=list[PropertyPhoto], operation_id="get_property_photos")
async def get_property_photos(property_id: str, current_user: dict = Depends(get_current_user)):
    """
    Gets all photos for a property
    """
    try:
        photos = PropertyService.get_property_photos(property_id)
        if len(photos) == 0:
            return []
        return [photo.model_dump() for photo in photos]
    except Exception as e:
        logging.error(f"Error in get_property_photos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
