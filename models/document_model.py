import ormar
from typing import Optional, TYPE_CHECKING
from db_config import base_ormar_config
from models.base_model import BaseModel
from models.property_model import Property


class Document(ormar.Model):

    class Meta(BaseModel.Meta):
        tablename = "documents"

    file_id: str = ormar.String(max_length=100)
    file_url: str = ormar.String(max_length=255)

    primary: bool = ormar.Boolean(default=False)

    # property: Optional[Property] = ormar.ForeignKey(Property, nullable=True)
