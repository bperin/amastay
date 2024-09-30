from pydantic import BaseModel
from typing import Literal

class AIMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    class Config:
        frozen = True