import asyncio
from uuid import UUID

from neo4j import AsyncResult, AsyncSession

from app.models.controller import ControllerDataModel


class LinkDispatcher:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def make_request(self, query: str, **kwargs) -> AsyncResult:
        try:
            result: AsyncResult = await self.session.run(query=query, **kwargs)
        except asyncio.CancelledError:
            self.session.cancel()
            raise
        else:
            return result

    async def link_controller_to_block(self, controller_id: str, block_id: str):
        query = """
            MATCH (cc:Controller) WHERE cc.id = $controller_id
            MATCH (bb:Block) WHERE bb.id = $block_id
            CREATE (cc)-[:LINKED_BLOCK]->(bb)
            RETURN count(cc) as linked_controllers
        """

        result = await self.make_request(
            query=query, controller_id=controller_id, block_id=block_id
        )
        result_data = await result.single()
        return result_data["linked_controllers"]

    async def link_car_to_block(self, car_id: str, block_id: str):
        query = """
            MATCH (cc:Car) WHERE cc.id = $car_id
            MATCH (bb:Block) WHERE bb.id = $block_id
            CREATE (cc)-[:LINKED_CAR]->(bb)
            RETURN count(cc) as linked_cars
        """

        result = await self.make_request(query=query, car_id=car_id, block_id=block_id)
        result_data = await result.single()
        return result_data["linked_cars"]


async def get_car_linked_controllers(
    car_id: str, session: AsyncSession
) -> list[ControllerDataModel]:
    raise NotImplementedError()
    result = await make_request(
        session=session,
        query="MATCH (car:Car)-[:LINKED]->(blocks)<-[:LINKED]-(controllers) WHERE car.id = $car_id return controllers, blocks",
        car_id=car_id,
    )
    data = await result.data()
    if not data:
        return []
    return [ControllerDataModel(**item.get("controllers")) for item in data]
