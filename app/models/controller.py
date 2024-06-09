from pydantic import BaseModel

from app.models.mixins import IDMixin


class BareControllerModel(BaseModel):
    controller_name: str


class ControllerCreateModel(BareControllerModel):
    data: bytes


class ControllerDataModel(ControllerCreateModel, IDMixin):
    pass


class BareIDControllerModel(BareControllerModel, IDMixin):
    pass
