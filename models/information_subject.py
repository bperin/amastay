# models/information_subject.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class InformationSubject(BaseModel):
    id: UUID
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
