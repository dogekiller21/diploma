from pydantic import BaseModel, ConfigDict

from app.models.mixins import IDMixin


class BlockCreateModel(BaseModel):
    block_name: str
    model_name: str

    model_config = ConfigDict(protected_namespaces=())


class BlockDataModel(BlockCreateModel, IDMixin):
    pass
