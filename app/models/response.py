from pydantic import model_validator

from app.models.block import BlockDataModel
from app.models.controller import BareIDControllerModel, ControllerDataModel


class BlockControllersResponseModel(BlockDataModel):
    firmwares: list[BareIDControllerModel]
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
