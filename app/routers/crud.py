from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from db.crud.car import create_car_object, get_car_object_by_numberplate, delete_car_object_by_id
from db.models.car import CarCreateModel, CarDataModel
from db.session import get_db_session

router = APIRouter(prefix="/crud")


@router.post("/car")
async def create_car(
    data: CarCreateModel, session=Depends(get_db_session)
) -> CarDataModel:
    return await create_car_object(data=data, session=session)


@router.get("/car")
async def get_car_by_numberplate(
    numberplate: str, session=Depends(get_db_session)
) -> CarDataModel | None:
    return await get_car_object_by_numberplate(numberplate=numberplate, session=session)


@router.delete("/car")
async def delete_car_by_id(
    internal_id: Annotated[UUID, Query(alias="id")], session=Depends(get_db_session)
) -> int:
    return await delete_car_object_by_id(internal_id=internal_id, session=session)
