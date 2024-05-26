from neo4j import AsyncSession

from app.db.crud.requests import make_request
from app.models.car import ControllerDataModel


async def create_controller_link(
    controller_id: str, block_id: str, session: AsyncSession
) -> None:
    await make_request(
        session=session,
        query="MATCH (cc:Controller) WHERE cc.id = $controller_id "
        "MATCH (bb:Block) WHERE bb.id = $block_id CREATE "
        "(cc)-[:LINKED]->(bb)",
        controller_id=controller_id,
        block_id=block_id,
    )
    return


async def create_car_link(car_id: str, block_id: str, session: AsyncSession) -> None:
    await make_request(
        session=session,
        query="MATCH (cc:Car) WHERE cc.id = $car_id "
        "MATCH (bb:Block) WHERE bb.id = $block_id CREATE "
        "(cc)-[:LINKED]->(bb)",
        car_id=car_id,
        block_id=block_id,
    )
    return


async def get_block_linked_controllers(
    block_id: str, session: AsyncSession
) -> list[ControllerDataModel]:
    result = await make_request(
        session=session,
        query="MATCH (cc:Controller)-[:LINKED]->(blocks:Block) WHERE blocks.id = $block_id return cc",
        block_id=block_id,
    )
    data = await result.data()
    if not data:
        return []
    return [ControllerDataModel(**item.get("cc")) for item in data]


async def get_car_linked_controllers(
    car_id: str, session: AsyncSession
) -> list[ControllerDataModel]:
    result = await make_request(
        session=session,
        query="MATCH (car:Car)-[:LINKED]->(blocks)<-[:LINKED]-(controllers) WHERE car.id = $car_id return controllers, blocks",
        car_id=car_id,
    )
    data = await result.data()
    if not data:
        return []
    return [ControllerDataModel(**item.get("controllers")) for item in data]
