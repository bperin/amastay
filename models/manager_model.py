from typing import Optional, List
from pydantic import BaseModel
from models import *


class Manager(BaseModel):
    """Manager model representing property managers"""

    id: str = None
    first_name: str = None
    last_name: Optional[str] = None
    email: str = None
    phone: str = None
    verified: bool = False
    phone_verified: bool = False
    created_at: str = None
    updated_at: str = None

    # Relationships
    properties: Optional[List["Property"]] = []


class CreateManager(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    phone: str


class UpdateManager(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
