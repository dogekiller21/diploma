import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
from starlette.requests import Request

from app.db.neo4j.car.storage import CarStorage
from app.db.neo4j.links.storage import LinkStorage
from app.db.neo4j.session import build_storage_dependency
from app.models.car import CarCreateModel, CarDataModel, CarDeleteModel
from app.models.controller import ControllerDataModel
from app.models.response import CarBlockResponseModel

router = APIRouter(prefix="/car", tags=["car"])

logger = logging.getLogger(__name__)


@router.post("/", name="add_car")
async def create_car(
    data: CarCreateModel,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel:
    try:
        return await storage.create_car_object(data=data)
    except Exception as e:
        logger.error("Error creating car object: %s", e, exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Серверная ошибка при создании авто! Обратитесь к администратору",
        )


@router.get("/firmware")
async def get_car_firmware(
    car_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    try:
        return await storage.get_car_linked_controllers(car_id=car_id)
    except Exception as e:
        logger.error("Error getting car firmwares: %s", e, exc_info=e)
        return []


@router.get("/")
async def get_car_by_numberplate(
    numberplate: str,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel | None:
    try:
        return await storage.get_car_object_by_numberplate(numberplate=numberplate)
    except Exception as e:
        logger.error("Error getting car by numberplate: %s", e, exc_info=e)
        return None


@router.delete("/", name="delete_car")
async def delete_car_by_id(
    data: CarDeleteModel,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> int:
    try:
        return await storage.delete_car_object_by_id(internal_id=str(data.id))
    except Exception as e:
        logger.error("Error deleting car by id: %s", e, exc_info=e)
        return 0


@router.get("/full", name="get_cars_full")
async def get_cars_full(
    block: str | None = None,
    car: str | None = None,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> list[CarBlockResponseModel]:
    try:
        return await storage.get_cars_with_blocks_response(
            limit=100, offset=0, block_id=block, car_id=car
        )
    except Exception as e:
        logger.error("Error getting cars full: %s", e, exc_info=e)
        return []
