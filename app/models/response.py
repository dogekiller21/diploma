from pydantic import BaseModel, model_validator

from app.models.block import BlockDataModel
from app.models.controller import (
    BlockControllerResponseModel,
    ControllerDataModel,
    SingleBlockControllerResponseModel,
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


class ControllerResponseModel(ControllerDataModel):
    block: BlockDataModel
    cars_count: int


class ControllerVersionsResponseModel(BaseModel):
    controller: ControllerResponseModel


class BaseResponse(BaseModel):
    success: bool
    message: str | None = None


class FirmwareResponse(BaseResponse):

    firmware: SingleBlockControllerResponseModel | None = None


class FirmwareVersionResponse(BaseResponse):

    version: VersionResponseModel | None = None
