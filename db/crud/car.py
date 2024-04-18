from uuid import UUID

from neo4j import AsyncSession

from db.crud.requests import make_request
from db.models.car import CarCreateModel, CarDataModel


async def create_car_object(
    data: CarCreateModel, session: AsyncSession
) -> CarDataModel:
    # TODO: запретить создавать несколько машин с одним номером
    result = await make_request(
        session=session,
        query="CREATE (cc:Car {id: randomUUID(), numberplate: $numberplate, info: $info}) RETURN cc.id AS id",
        numberplate=data.numberplate,
        info=data.info,
    )
    record = await result.single()
    record_data = record.data()
    record_data.update(data.dict())
    return CarDataModel(**record_data)


async def get_car_object_by_numberplate(
    numberplate: str, session: AsyncSession
) -> CarDataModel | None:
    result = await make_request(
        session=session,
        query="MATCH (cc:Car) WHERE cc.numberplate = $numberplate RETURN cc.id as id, cc.numberplate as numberplate, cc.info as info",
        numberplate=numberplate
    )
    record = await result.single()
    if record is None:
        return None
    record_data = record.data()
    return CarDataModel(**record_data)


async def get_car_object_by_id(
    internal_id: UUID, session: AsyncSession
) -> CarDataModel | None:
    result = await make_request(
        session=session,
        query="MATCH (cc:Car) WHERE cc.id = $id RETURN cc.id as id, cc.numberplate as numberplate, cc.info as info",
        id=str(internal_id)
    )
    record = await result.single()
    record_data = record.data()
    return CarDataModel(**record_data)


async def delete_car_object_by_id(
    internal_id: UUID, session: AsyncSession
) -> int:
    """Возвращает кол-во удаленных записей"""
    result = await make_request(
        session=session,
        query="MATCH (cc:Car) WHERE cc.id = $id DETACH DELETE cc RETURN count(cc) as items_deleted",
        id=str(internal_id)
    )
    record = await result.single()
    items_deleted = record["items_deleted"]
    return items_deleted
