from uuid import UUID

from app.db.neo4j.base.storage import BaseStorage
from app.models.car import CarCreateModel, CarDataModel
from app.models.response import CarBlockResponseModel


class CarStorage(BaseStorage):
    async def create_car_object(
        self,
        data: CarCreateModel,
    ) -> CarDataModel:
        query = """
        CREATE
        (cc:Car {
            id: randomUUID(),
            numberplate: $numberplate,
            brand: $brand,
            model: $model,
            info: $info
            })
        RETURN cc.id AS id
        """

        # TODO: запретить создавать несколько машин с одним номером
        result = await self.make_request(query=query, **data.dict())
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        return CarDataModel.model_validate(record_data)

    async def get_car_object_by_numberplate(
        self,
        numberplate: str,
    ) -> CarDataModel | None:
        query = """
            MATCH (cc:Car)
            WHERE cc.numberplate = $numberplate
            RETURN
            cc.id as id,
            cc.numberplate as numberplate,
            cc.brand as brand,
            cc.model as model,
            cc.info as info
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
        query = """
            MATCH (cc:Car)
            WHERE cc.id = $id
            RETURN
            cc.id as id,
            cc.numberplate as numberplate,
            cc.brand as brand,
            cc.model as model,
            cc.info as info
        """
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

    async def get_cars_with_blocks_response(
        self,
        limit: int,
        offset: int,
        block_id: str | None = None,
        car_id: str | None = None,
    ) -> list[CarBlockResponseModel]:
        query = """
        MATCH (car:Car)
        """
        if car_id:
            query += """
            WHERE car.id = $car_id
            """
        query += """
        OPTIONAL MATCH (car)-[:LINKED_CAR]->(bb:Block)
        """
        if block_id:
            query += """
            WHERE bb.id = $block_id
            """
        query += """
        OPTIONAL MATCH (cc:Controller)-[:LINKED_BLOCK]->(bb)
        WITH car, bb, COUNT(DISTINCT cc) as firmwares_count
        WITH car, COLLECT(DISTINCT {
            id: bb.id,
            block_name: bb.block_name,
            model_name: bb.model_name,
            firmwares_count: firmwares_count
        }) as blocks
        RETURN
            car.id as id,
            car.numberplate as numberplate,
            car.brand as brand,
            car.model as model,
            car.info as info,
            CASE WHEN SIZE(blocks) = 1 AND blocks[0].id IS NULL THEN [] ELSE blocks END as blocks
        SKIP $offset
        LIMIT $limit

        """

        result = await self.make_request(
            query=query, limit=limit, offset=offset, block_id=block_id, car_id=car_id
        )
        data = await result.data()
        print(f"{data=}")
        if not data:
            return []
        return [CarBlockResponseModel.model_validate(item) for item in data]
