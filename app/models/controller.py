from pydantic import BaseModel

from app.models.block import BlockDataModel
from app.models.mixins import IDMixin
from app.models.versions import VersionCreateModel, VersionResponseModel


class ControllerCreateModel(BaseModel):
    controller_name: str


class ControllerVersionCreateModel(ControllerCreateModel):
    version: VersionCreateModel


class ControllerDataModel(ControllerCreateModel, IDMixin):
    pass


class BlockControllerResponseModel(ControllerDataModel):
    first_version: VersionResponseModel


class SingleControllerDataModel(ControllerDataModel):
    first_version: VersionResponseModel
    versions: list[VersionResponseModel]
    block: BlockDataModel


class ControllerDeleteModel(IDMixin):
    pass
