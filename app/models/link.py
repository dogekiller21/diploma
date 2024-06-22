from pydantic import BaseModel

from app.models.block import ModalBlockCreateModel


class CarBlockLinkModel(BaseModel):
    car_id: str
    block: ModalBlockCreateModel


class CarBlockUnLinkModel(BaseModel):
    car_id: str
    block_id: str
