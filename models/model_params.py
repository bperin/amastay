from pydantic import BaseModel
from typing import Optional

class ModelParams(BaseModel):
    id: str
    prompt: str
    top_p: float
    temperature: float
    active: bool
    created_at: str
