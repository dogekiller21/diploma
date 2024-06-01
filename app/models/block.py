from pydantic import BaseModel

from app.models.mixins import IDMixin


class BlockCreateModel(BaseModel):
    block_name: str
    model_name: str


class BlockDataModel(BlockCreateModel, IDMixin):
    pass
