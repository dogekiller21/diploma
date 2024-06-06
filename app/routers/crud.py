from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from app.db.block.storage import BlockStorage
from app.db.car.storage import CarStorage
from app.db.controller.storage import ControllerStorage
from app.db.links.dispatcher import LinkDispatcher
from app.db.links.storage import LinkStorage
from app.db.session import build_dispatcher_dependency, build_storage_dependency
from app.models.block import BlockCreateModel, BlockDataModel
from app.models.car import CarCreateModel, CarDataModel
from app.models.controller import ControllerCreateModel, ControllerDataModel

router = APIRouter(prefix="/crud")


@router.post("/car")
async def create_car(
    data: CarCreateModel,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel:
    return await storage.create_car_object(data=data)


@router.post("/block")
async def create_block(
    data: BlockCreateModel,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> BlockDataModel:
    return await storage.create_block_object(data=data)


@router.post("/controller")
async def create_controller(
    data: ControllerCreateModel,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> ControllerDataModel:
    return await storage.create_controller_object(data=data)


@router.post("/link_controller")
async def link_controller_to_block(
    controller_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_controller_to_block(
        controller_id=controller_id,
        block_id=block_id,
    )


@router.post("/link_car")
async def link_car(
    car_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_car_to_block(car_id=car_id, block_id=block_id)


@router.get("/block_controllers")
async def get_block_controllers(
    block_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_block_linked_controllers(block_id=block_id)


@router.get("/car_controllers")
async def get_car_controllers(
    car_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_car_linked_controllers(car_id=car_id)


@router.get("/car")
async def get_car_by_numberplate(
    numberplate: str,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel | None:
    return await storage.get_car_object_by_numberplate(numberplate=numberplate)


@router.get("/controller_data")
async def get_controller_data(
    controller_id: str,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> list[bytes] | None:
    return await storage.get_controller_data(controller_id=controller_id)


@router.delete("/car")
async def delete_car_by_id(
    internal_id: Annotated[str, Query(alias="id")],
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> int:
    return await storage.delete_car_object_by_id(internal_id=internal_id)
