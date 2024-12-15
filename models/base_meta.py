import ormar
from db_config import base_ormar_config


class BaseMeta(ormar.ModelMeta):
    metadata = base_ormar_config.metadata
    database = base_ormar_config.database
