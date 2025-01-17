from typing import Optional, List
from pydantic import BaseModel, Field


class Guest(BaseModel):
    """Model representing a guest in the system"""

    id: str = ""
    phone: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class CreateGuest(BaseModel):
    phone: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateGuest(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
