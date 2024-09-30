from pydantic import BaseModel
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Choice:
    index: int
    message: Message
    logprobs: Optional[dict] = None
    finish_reason: Optional[str] = None

@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class ModelResponse:
    object: str
    id: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Choice]
    usage: Usage