from pydantic import BaseModel

from app.models.mixins import IDMixin


class CarCreateModel(BaseModel):
    numberplate: str
    info: str


class CarDataModel(CarCreateModel, IDMixin):
    pass
