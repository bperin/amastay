# models/recommendation_subjects_join.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class RecommendationSubjectsJoin(BaseModel):
    id: UUID
    recommendation_id: Optional[UUID]
    subject_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
