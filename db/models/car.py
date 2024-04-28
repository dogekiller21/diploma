from uuid import UUID

from pydantic import BaseModel


class CarCreateModel(BaseModel):
    numberplate: str
    info: str


class BlockCreateModel(BaseModel):
    block_name: str
    data: bytes


class ControllerCreateModel(BaseModel):
    controller_name: str


class CarDataModel(BaseModel):
    numberplate: str
    info: str
    id: UUID


class BlockDataModel(BaseModel):
    block_name: str
    data: bytes
    id: UUID


class ControllerDataModel(BaseModel):
    controller_name: str
    id: UUID
