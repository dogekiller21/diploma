from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from app.db.block.storage import BlockStorage
from app.db.car.storage import CarStorage
from app.db.controller.storage import ControllerStorage
from app.db.session import build_storage_dependency, get_db_session
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
async def link_controller(
    controller_id: str, block_id: str, session=Depends(get_db_session)
) -> None:
    return await create_controller_link(
        controller_id=controller_id, block_id=block_id, session=session
    )


@router.post("/link_car")
async def link_car(car_id: str, block_id: str, session=Depends(get_db_session)) -> None:
    return await create_car_link(car_id=car_id, block_id=block_id, session=session)


@router.get("/block_controllers")
async def get_block_controllers(
    block_id: str, session=Depends(get_db_session)
) -> list[ControllerDataModel]:
    return await get_block_linked_controllers(block_id=block_id, session=session)


@router.get("/car_controllers")
async def get_car_controllers(
    car_id: str, session=Depends(get_db_session)
) -> list[ControllerDataModel]:
    return await get_car_linked_controllers(car_id=car_id, session=session)


@router.get("/car")
async def get_car_by_numberplate(
    numberplate: str, session=Depends(get_db_session)
) -> CarDataModel | None:
    return await get_car_object_by_numberplate(numberplate=numberplate, session=session)


@router.get("/controller_data")
async def get_controller_data(
    controller_id: str, session=Depends(get_db_session)
) -> list[bytes] | None:
    return await get_controller_block_data(controller_id=controller_id, session=session)


@router.delete("/car")
async def delete_car_by_id(
    internal_id: Annotated[UUID, Query(alias="id")], session=Depends(get_db_session)
) -> int:
    return await delete_car_object_by_id(internal_id=internal_id, session=session)
