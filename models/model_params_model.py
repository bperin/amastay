from sqlmodel import Field
from models.base_model import BaseModel


class ModelParams(BaseModel, table=True):
    """Model representing AI model parameters"""

    __tablename__ = "model_params"

    prompt: str = Field()  # SQLModel will use Text type for str without max_length
    top_p: float = Field()
    temperature: float = Field()
    active: bool = Field(default=False)
