from pydantic import BaseModel, ConfigDict, model_validator

from app.models.block import BlockDataModel
from app.models.car import CarDataModel
from app.models.controller import (
    BlockControllerResponseModel,
    ControllerDataModel,
    SingleControllerDataModel,
)
from app.models.versions import VersionResponseModel


class BlockControllersResponseModel(BlockDataModel):
    firmwares: list[BlockControllerResponseModel]
    cars_count: int
    firmware_count: int | None = None

    @model_validator(mode="after")
    @classmethod
    def set_additional_info(cls, values):
        if values.firmware_count is None:
            values.firmware_count = len(values.firmwares)
        return values


class BlockResponseModel(BaseModel):
    id: str
    block_name: str
    model_name: str
    firmwares_count: int

    model_config = ConfigDict(protected_namespaces=())


class CarBlockResponseModel(CarDataModel):
    blocks: list[BlockResponseModel]
    blocks_count: int = None

    @model_validator(mode="after")
    @classmethod
    def set_additional_info(cls, values):
        if values.blocks_count is None:
            values.blocks_count = len(values.blocks)
        return values


class ControllerResponseModel(ControllerDataModel):
    block: BlockDataModel
    cars_count: int


class ControllerVersionsResponseModel(BaseModel):
    controller: ControllerResponseModel


class BaseAPIResponse(BaseModel):
    success: bool
    message: str | None = None


class FirmwareAPIResponse(BaseAPIResponse):
    firmware: SingleControllerDataModel | None = None


class FirmwareVersionAPIResponse(BaseAPIResponse):

    version: VersionResponseModel | None = None
