from pydantic import BaseModel

from app.models.mixins import IDMixin


class CarCreateModel(BaseModel):
    numberplate: str
    brand: str
    model: str
    info: str | None = None


class CarDataModel(CarCreateModel, IDMixin):
    pass


class CarDeleteModel(IDMixin):
    pass
