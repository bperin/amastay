from pydantic import BaseModel
from typing import Optional


class PropertyPhoto(BaseModel):
    """Model representing property photos"""

    id: str = ""
    property_id: str = ""
    url: str = ""
    gs_uri: str = ""
    created_at: str = ""
    updated_at: str = ""

    class Config:
        from_attributes = True
