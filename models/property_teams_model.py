from typing import Optional
from pydantic import BaseModel, Field


class PropertyTeam(BaseModel):
    id: str = None
    property_id: str = None
    team_id: str = None
    created_at: str = None
    updated_at: str = None

    property_: Optional["Property"] = Field(default=None, alias="property")
    team: Optional["Team"] = None


class CreatePropertyTeam(BaseModel):
    property_id: str
    team_id: str
