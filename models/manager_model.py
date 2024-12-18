from typing import Optional, List
from pydantic import BaseModel, Field
from models import *


class Manager(BaseModel):
    """Manager model representing property managers"""

    id: str = ""
    first_name: str = ""
    last_name: Optional[str] = None
    email: str = ""
    phone: str = ""
    verified: bool = False
    phone_verified: bool = False
    created_at: str = ""
    updated_at: str = ""

    # Relationships with Field alias
    properties: List["Property"] = Field(default_factory=list)


class CreateManager(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: str


class ManagerInvite(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: str
    team_id: Optional[str] = None


class UpdateManager(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
