from pydantic import BaseModel
from typing import Optional


class InformationSubject(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
