from pydantic import BaseModel


class PropertyTeams(BaseModel):
    id: str
    property_id: str
    team_id: str
    created_at: str
    updated_at: str
