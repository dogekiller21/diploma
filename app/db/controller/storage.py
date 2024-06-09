from uuid import UUID

from app.db.base.storage import BaseStorage
from app.models.controller import ControllerCreateModel, ControllerDataModel
from app.models.response import ControllerResponseModel


class ControllerStorage(BaseStorage):
    async def create_controller_object(
        self,
        data: ControllerCreateModel,
    ) -> ControllerDataModel:
        query = """
        CREATE
        (cc:Controller {id: randomUUID(), controller_name: $controller_name, data: $data})
        RETURN cc.id AS id
        """
        result = await self.make_request(
            query=query,
            controller_name=data.controller_name,
            data=data.data,
        )
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        return ControllerDataModel.model_validate(record_data)

    async def get_controller_data(self, controller_id: str) -> list[bytes] | None:
        result = await self.make_request(
            query="MATCH (cc:Controller) WHERE cc.id = $controller_id RETURN cc.data as data",
            controller_id=controller_id,
        )
        data = await result.data()
        if not data:
            return None
        return data[0]["data"]

    async def get_controllers_response(
        self, limit: int, offset: int, block_id: str | None = None
    ) -> list[ControllerResponseModel]:
        db_query = """
            MATCH (cc:Controller)-[:LINKED_BLOCK]->(bb:Block)<-[:LINKED_CAR]-(car:Car)

        """
        if block_id is not None:
            db_query += f"""
             WHERE
             bb.id = $block_id
        """

        db_query += """
            RETURN
            cc.data as data,
            cc.controller_name as controller_name,
            cc.id as id,
            bb as block,
            count(DISTINCT car) as cars_count
            SKIP $offset
            LIMIT $limit
        """

        result = await self.make_request(
            query=db_query,
            limit=limit,
            offset=offset,
        )
        data = await result.data()
        if not data:
            return []
        return [ControllerResponseModel.model_validate(item) for item in data]
