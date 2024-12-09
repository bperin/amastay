from pydantic import BaseModel
from typing import Literal


class HfMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

    @classmethod
    def create(cls, role: str, content: str):
        return cls(role=role, content=[{"text": content}])
