from uuid import UUID

from app.db.neo4j.base.storage import BaseStorage
from app.models.car import CarCreateModel, CarDataModel


class CarStorage(BaseStorage):
    async def create_car_object(
        self,
        data: CarCreateModel,
    ) -> CarDataModel:
        query = "CREATE (cc:Car {id: randomUUID(), numberplate: $numberplate, info: $info}) RETURN cc.id AS id"
        # TODO: запретить создавать несколько машин с одним номером
        result = await self.make_request(
            query=query,
            numberplate=data.numberplate,
            info=data.info,
        )
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        return CarDataModel(**record_data)

    async def get_car_object_by_numberplate(
        self,
        numberplate: str,
    ) -> CarDataModel | None:
        query = """
            MATCH (cc:Car) WHERE cc.numberplate = $numberplate
            RETURN cc.id as id, cc.numberplate as numberplate, cc.info as info
        """
        result = await self.make_request(
            query=query,
            numberplate=numberplate,
        )
        record = await result.single()
        if record is None:
            return None
        record_data = record.data()
        return CarDataModel(**record_data)

    async def get_car_object_by_id(
        self,
        internal_id: UUID,
    ) -> CarDataModel | None:
        query = "MATCH (cc:Car) WHERE cc.id = $id RETURN cc.id as id, cc.numberplate as numberplate, cc.info as info"
        result = await self.make_request(
            query=query,
            id=str(internal_id),
        )
        record = await result.single()
        record_data = record.data()
        return CarDataModel(**record_data)

    async def delete_car_object_by_id(self, internal_id: str) -> int:
        """Возвращает кол-во удаленных записей"""
        query = "MATCH (cc:Car) WHERE cc.id = $id DETACH DELETE cc RETURN count(cc) as items_deleted"
        result = await self.make_request(
            query=query,
            id=str(internal_id),
        )
        record = await result.single()
        items_deleted = record["items_deleted"]
        return items_deleted
