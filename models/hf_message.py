from pydantic import BaseModel
from typing import Dict, List, Literal


class HfMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: List[Dict[str, str]]

    @classmethod
    def create(cls, role: str, content: str):
        return cls(role=role, content=[{"text": content}])
