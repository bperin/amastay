from pydantic import BaseModel
from typing import Literal, List


class ContentItem(BaseModel):
    text: str


class HfMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: List[ContentItem]

    class Config:
        frozen = True

    @classmethod
    def create(cls, role: str, text: str):
        return cls(role=role, content=[ContentItem(text=text)])
