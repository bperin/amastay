from pydantic import BaseModel
from typing import Optional


class PropertyMetadata(BaseModel):
    """Model representing a property metadata in the system"""

    id: str = None
    property_id: str = None
    data: dict = None
    updated_at: str = None
    created_at: str = None
    scraped: bool = None
    property: Optional["Property"] = None

    class Config:
        from_attributes = True


class ScrapeAsyncResponse(BaseModel):
    """Response model for property scraping endpoint"""

    message: str
    property_id: str
    status: str
