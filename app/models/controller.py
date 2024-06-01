from pydantic import BaseModel

from app.models.mixins import IDMixin


class ControllerCreateModel(BaseModel):
    controller_name: str
    data: bytes


class ControllerDataModel(ControllerCreateModel, IDMixin):
    pass
