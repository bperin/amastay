# models/property_information_subject.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class PropertyInformationSubject(BaseModel):
    id: UUID
    property_information_id: Optional[UUID]
    subject_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
