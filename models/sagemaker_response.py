from typing import List, Optional
from pydantic import BaseModel


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Message(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    index: int
    message: Message
    logprobs: Optional[None]
    finish_reason: str


class SageMakerResponse(BaseModel):
    object: str
    id: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Choice]
    usage: Usage
