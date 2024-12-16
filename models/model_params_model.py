import ormar
from typing import Optional
from db_config import base_ormar_config
from models.base_model import BaseModel


class ModelParams(ormar.Model):

    class Meta(BaseModel.Meta):
        tablename = "model_params"

    prompt: str = ormar.Text()
    top_p: float = ormar.Float()
    temperature: float = ormar.Float()
    active: bool = ormar.Boolean(default=False)
