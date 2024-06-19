from app.db.neo4j.base.storage import BaseStorage
from app.models.controller import ControllerCreateModel, ControllerDataModel
from app.models.response import BlockControllerResponseModel


class ControllerStorage(BaseStorage):
    async def create_controller_object(
        self,
        data: ControllerCreateModel,
    ) -> ControllerDataModel:
        query = """
            CREATE
            (cc:Controller {id: randomUUID(), controller_name: $controller_name})
            RETURN cc.id AS id
        """
        result = await self.session.run(query, controller_name=data.controller_name)
        # result = await self.make_request(
        #     query=query,
        #     controller_name=data.controller_name,
        # )
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        return ControllerDataModel.model_validate(record_data)

    async def delete_firmware_by_id(self, firmware_id: str) -> int:
        query = """
            MATCH (cc:Controller)
            WHERE cc.id = $firmware_id
            OPTIONAL MATCH (cc)-[:LINKED_VERSION*]->(version)
            
            DETACH DELETE cc, version
            RETURN count(cc) + count(version) as items_deleted
        """
        result = await self.make_request(
            query=query,
            firmware_id=firmware_id,
        )
        data = await result.single()
        return data.data()["items_deleted"]

    async def get_controllers_response(
        self, limit: int, offset: int, block_id: str | None = None
    ) -> list[BlockControllerResponseModel]:
        db_query = """
            MATCH (vv:Version)<-[:LINKED_VERSION]-(cc:Controller)-[:LINKED_BLOCK]->(bb:Block)<-[:LINKED_CAR]-(car:Car)

        """
        if block_id is not None:
            db_query += f"""
                WHERE
                bb.id = $block_id
            """

        # noinspection SqlNoDataSourceInspection
        db_query += """
            WITH 
                cc.data as data,
                cc.controller_name as controller_name,
                cc.id as id,
                bb as block,
                collect(DISTINCT {
                    id: vv.id,
                    version_name: vv.name,
                    release_date: vv.release_date
                }) as versions,
                count(DISTINCT car) as cars_count
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
        return [BlockControllerResponseModel.model_validate(item) for item in data]
