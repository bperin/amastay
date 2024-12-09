from pydantic import BaseModel
from typing import Dict, List


class SystemPrompt(BaseModel):
    text: str

    def to_dict(self) -> Dict[str, str]:
        return {"text": self.text}

    @classmethod
    def create(cls, prompt: str) -> List[Dict[str, str]]:
        return [cls(text=prompt).to_dict()]
