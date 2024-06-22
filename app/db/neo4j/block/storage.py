import logging

from app.db.neo4j.base.storage import BaseStorage
from app.models.block import BlockCreateModel, BlockDataModel
from app.models.response import BlockControllersResponseModel

logger = logging.getLogger(__name__)


class BlockStorage(BaseStorage):

    async def get_block_by_id(self, block_id: str) -> BlockDataModel | None:
        query = "MATCH (bb:Block) WHERE bb.id = $block_id RETURN bb"
        result = await self.make_request(
            query=query,
            block_id=block_id,
        )
        data = await result.data()
        if not data:
            return None
        return BlockDataModel.model_validate(data[0].get("bb"))

    async def create_block_object(
        self,
        data: BlockCreateModel,
    ) -> BlockDataModel:
        print(f"{data=}")
        query = """
        CREATE (bb:Block {id: randomUUID(), block_name: $block_name, model_name: $model_name})
        RETURN bb.id as id, bb.block_name as block_name, bb.model_name as model_name
        """
        result = await self.make_request(
            query=query,
            **data.model_dump(),
        )
        record = await result.single()
        return BlockDataModel.model_validate(record.data())

    async def delete_block_by_id(self, block_id: str) -> int:
        query = """
            MATCH (bb:Block)
            WHERE bb.id = $block_id
            OPTIONAL MATCH (bb)<-[r:LINKED_BLOCK*]-(controllers)
            OPTIONAL MATCH (controllers)-[:LINKED_VERSION*]->(version)
            
            DETACH DELETE bb, controllers, version
            RETURN count(bb) + count(controllers) + count(version) as items_deleted
        """
        result = await self.make_request(
            query=query,
            block_id=block_id,
        )
        data = await result.single()
        return data.data()["items_deleted"]

    async def get_blocks_response(
        self,
        limit: int,
        offset: int,
        query: str | None = None,
    ) -> list[BlockDataModel]:
        db_query = """
            MATCH (bb:Block)
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
        logger.info(f"blocks data: {data}")
        if not data:
            return []
        return [BlockDataModel.model_validate(item["bb"]) for item in data]

    async def get_block_with_controllers_response(
        self,
        limit: int,
        offset: int,
        block_id: str | None = None,
        car_id: str | None = None,
    ) -> list[BlockControllersResponseModel]:
        """
        {
            'id': 'd74c0902-9db8-4f20-bb0d-2127d0e66719',
            'block_name': 'block1',
            'model_name': 'model1',
            'firmwares': [
                {
                    'id': '1350e832-b62d-456b-8b24-cc487be50737',
                    'first_version': {
                        'version': '0.1b',
                        'id': 'efe54bb2-8c4b-4d0d-b8df-03720ca0f801',
                        'release_date': '2024-02-01'
                    },
                    'controller_name': 'controller1'
                }
            ],
            'cars_count': 0
        }


        :param car_id: str
        :param limit: int
        :param offset: int
        :param block_id: str
        :return: list[BlockControllersResponseModel]
        """
        if not block_id:
            block_id = None

        if not car_id:
            car_id = None

        db_query = """
MATCH (bb:Block)
WHERE ($block_id IS NULL OR bb.id = $block_id)
OPTIONAL MATCH (car:Car)-[:LINKED_CAR]->(bb)
WHERE ($car_id IS NULL OR car.id = $car_id)
WITH bb, car
WHERE $car_id IS NULL OR car IS NOT NULL
MATCH (cc:Controller)-[:LINKED_BLOCK]->(bb)
MATCH (vv:Version)<-[:LINKED_VERSION]-(cc)
WITH bb, cc, bb.id AS id, bb.block_name AS block_name, bb.model_name AS model_name, collect(DISTINCT vv) AS versions, count(DISTINCT car) AS cars_count
UNWIND versions AS v
WITH id, block_name, model_name, cc, v, cars_count
ORDER BY v.release_date DESC
WITH id, block_name, model_name, cc, collect(v)[0] AS first_version, cars_count
WITH id, block_name, model_name, cars_count, collect(DISTINCT {
    id: cc.id,
    controller_name: cc.controller_name,
    first_version: {
        id: first_version.id,
        version: first_version.version,
        release_date: first_version.release_date
    }
}) AS firmwares
RETURN id, block_name, model_name, firmwares, cars_count
SKIP $offset
LIMIT $limit

        """
        result = await self.make_request(
            query=db_query, limit=limit, offset=offset, block_id=block_id, car_id=car_id
        )
        data = await result.data()
        if not data:
            return []
        return [BlockControllersResponseModel.model_validate(item) for item in data]
