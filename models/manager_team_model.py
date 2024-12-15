from pydantic import BaseModel


class ManagerTeams(BaseModel):
    id: str
    manager_id: str
    team_id: str
    created_at: str
    updated_at: str
