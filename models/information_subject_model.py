from pydantic import BaseModel
from typing import Optional


class InformationSubject(BaseModel):
    id: str = None
    name: str = None
    created_at: str = None
    updated_at: str = None
