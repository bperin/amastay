# models/document.py

import ormar
from typing import Optional
from db_config import base_ormar_config
from models.property import Property


class Document(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="documents")

    id: ormar.UUID = ormar.UUID(primary_key=True)

    file_id: str = ormar.String(max_length=100)
    file_url: str = ormar.String(max_length=255)

    primary: bool = ormar.Boolean(default=False)

    created_at: str = ormar.String(max_length=50)
    updated_at: str = ormar.String(max_length=50)

    property: Optional[Property] = ormar.ForeignKey(Property, nullable=True)
