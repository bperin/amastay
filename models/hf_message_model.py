from pydantic import BaseModel, Field
from typing import List, Literal, Union, Dict
from models.message_model import Message


class ImageUrlContent(BaseModel):
    type: Literal["image_url"]
    image_url: Dict[str, str]


class TextContent(BaseModel):
    type: Literal["text"]
    text: str


class HfMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: List[Union[TextContent, ImageUrlContent]]

    @classmethod
    def create_text(cls, text: str, role: str = "user") -> "HfMessage":
        """Create a simple text message"""
        return cls(role=role, content=[TextContent(type="text", text=text)])

    @classmethod
    def create_image(cls, image_url: str, text: str = None) -> "HfMessage":
        """Create an image message with optional text"""
        content = [ImageUrlContent(type="image_url", image_url={"url": image_url})]
        if text:
            content.append(TextContent(type="text", text=text))
        return cls(role="user", content=content)

    @classmethod
    def from_message(cls, message: Message) -> "HfMessage":
        """Convert a Message model to HfMessage format"""
        role = "user" if message.sender_type == 0 else "assistant"
        return cls.create_text(text=message.content, role=role)
