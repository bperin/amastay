# models/base_model.py
import uuid
from datetime import datetime
import ormar
from sqlalchemy import func  # Import SQLAlchemy functions for server defaults
from db_config import base_ormar_config


class BaseModel(ormar.Model):
    class Meta:
        pkname = "id"
        metadata = base_ormar_config.metadata
        database = base_ormar_config.database

    # Common Fields
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4, nullable=False)
    created_at: datetime = ormar.DateTime(server_default=func.now(), nullable=False)
    updated_at: datetime = ormar.DateTime(server_default=func.now(), server_onupdate=func.now(), nullable=False)
