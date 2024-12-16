from typing import Optional
from pydantic import BaseModel


class ModelParams(BaseModel):
    """Model representing AI model parameters"""

    id: str = ""
    prompt: str = ""
    top_p: float = 0.5
    temperature: float = 0.5
    active: bool = False
    created_at: str = None
    updated_at: str = None


class CreateModelParams(BaseModel):
    prompt: str
    top_p: float
    temperature: float
    active: bool


class UpdateModelParams(BaseModel):
    prompt: Optional[str] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    active: Optional[bool] = None
