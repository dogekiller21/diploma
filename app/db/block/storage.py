from app.db.base.storage import BaseStorage
from app.models.block import BlockCreateModel, BlockDataModel
from app.models.response import BlockControllersResponseModel


class BlockStorage(BaseStorage):
    async def create_block_object(
        self,
        data: BlockCreateModel,
    ) -> BlockDataModel:
        query = """
        CREATE (bb:Block {id: randomUUID(), block_name: $block_name, model_name: $model_name})
        RETURN bb
        """
        result = await self.make_request(
            query=query,
            **data.model_dump(),
        )
        record = await result.single()
        record_data = record.data()
        print(record_data)
        return BlockDataModel(**record_data["bb"])

    async def get_blocks_response(
        self,
        limit: int,
        offset: int,
        query: str | None = None,
    ) -> list[BlockDataModel]:
        db_query = """
            MATCH (bb:Block)<-[:LINKED_BLOCK]-(cc:Controller)
        """
        if query is not None:
            db_query += f"""
             WHERE
             bb.block_name CONTAINS $s_query
             OR bb.model_name CONTAINS $s_query
             
        """

        db_query += """
            RETURN DISTINCT bb
            SKIP $offset
            LIMIT $limit
        """

        result = await self.make_request(
            query=db_query,
            limit=limit,
            offset=offset,
            s_query=query,
        )
        data = await result.data()
        if not data:
            return []
        return [BlockDataModel.model_validate(item["bb"]) for item in data]

    async def get_block_with_controllers_response(
        self, limit: int, offset: int, block_id: str | None = None
    ) -> list[BlockControllersResponseModel]:
        db_query = """
            MATCH (cc:Controller)-[:LINKED_BLOCK]->(bb:Block)<-[:LINKED_CAR]-(car:Car)

        """
        if block_id:
            db_query += f"""
             WHERE
             bb.id = $block_id
        """

        db_query += """
            WITH 
                bb.id as id,
                bb.block_name as block_name,
                bb.model_name as model_name,
                collect(DISTINCT {
                    id: cc.id,
                    controller_name: cc.controller_name                
                }) as firmwares,
                count(DISTINCT car) as cars_count
            SKIP $offset
            LIMIT $limit
            RETURN 
                id,
                block_name,
                model_name,
                firmwares,
                cars_count
        """

        result = await self.make_request(
            query=db_query, limit=limit, offset=offset, block_id=block_id
        )
        data = await result.data()
        print(1)
        for item in data:
            print(item)
        if not data:
            return []
        return [BlockControllersResponseModel.model_validate(item) for item in data]
