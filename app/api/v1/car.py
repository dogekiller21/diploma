from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Body

from app.db.neo4j.car.storage import CarStorage
from app.db.neo4j.links import LinkStorage
from app.db.neo4j.session import build_storage_dependency
from app.models.car import CarCreateModel, CarDataModel
from app.models.controller import ControllerDataModel

router = APIRouter(prefix="/car", tags=["car"])


@router.post("/")
async def create_car(
    data: CarCreateModel,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel:
    return await storage.create_car_object(data=data)


@router.get("/firmware")
async def get_car_firmware(
    car_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_car_linked_controllers(car_id=car_id)


@router.get("/")
async def get_car_by_numberplate(
    numberplate: str,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel | None:
    return await storage.get_car_object_by_numberplate(numberplate=numberplate)


@router.delete("/")
async def delete_car_by_id(
    # TODO: тут нужна моделька, иначе будет просто "какой-то айди" вместо {"id": "какой-то айди"}
    internal_id: Annotated[str, Body(alias="id")],
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> int:
    return await storage.delete_car_object_by_id(internal_id=internal_id)
