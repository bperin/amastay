import ormar
from typing import Optional
from db_config import base_ormar_config


class ModelParams(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="model_params")

    id: ormar.UUID = ormar.UUID(primary_key=True)

    prompt: str = ormar.Text()
    top_p: float = ormar.Float()
    temperature: float = ormar.Float()
    active: bool = ormar.Boolean(default=False)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)
