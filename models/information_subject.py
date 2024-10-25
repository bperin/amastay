# models/information_subject.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class InformationSubject(BaseModel):
    id: UUID
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
