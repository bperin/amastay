from pydantic import BaseModel
from typing import Optional


class PropertyInformationSubject(BaseModel):
    id: str
    property_information_id: Optional[str]
    subject_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
