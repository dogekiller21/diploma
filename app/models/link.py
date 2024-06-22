from pydantic import BaseModel

from app.models.block import ModalBlockCreateModel


class CarBlockLinkModel(BaseModel):
    car_id: str
    block: ModalBlockCreateModel
