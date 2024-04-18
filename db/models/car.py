from uuid import UUID

from pydantic import BaseModel


class CarCreateModel(BaseModel):
    numberplate: str
    info: str


class CarDataModel(BaseModel):
    numberplate: str
    info: str
    id: UUID
