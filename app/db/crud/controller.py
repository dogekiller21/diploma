from neo4j import AsyncSession

from app.db.crud.requests import make_request
from app.models.controller import ControllerCreateModel, ControllerDataModel


async def create_controller_object(
    data: ControllerCreateModel, session: AsyncSession
) -> ControllerDataModel:
    query = """
    CREATE
    (cc:Controller {id: randomUUID(), controller_name: $controller_name, data: $data})
    RETURN cc.id AS id
    """
    result = await make_request(
        session=session,
        query=query,
        controller_name=data.controller_name,
        data=data.data,
    )
    record = await result.single()
    record_data = record.data()
    record_data.update(data.dict())
    return ControllerDataModel(**record_data)


async def get_controller_block_data(
    controller_id: str, session: AsyncSession
) -> list[bytes] | None:
    raise NotImplementedError()
    result = await make_request(
        session=session,
        query="MATCH (cc:Controller)-[:LINKED]-(blocks) WHERE cc.id = $controller_id RETURN blocks",
        controller_id=controller_id,
    )
    data = await result.data()
    if not data:
        return None
    return [block["blocks"]["data"] for block in data]
