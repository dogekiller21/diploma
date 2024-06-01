from neo4j import AsyncSession

from app.db.crud.requests import make_request
from app.models.block import BlockCreateModel, BlockDataModel


async def create_block_object(
    data: BlockCreateModel, session: AsyncSession
) -> BlockDataModel:
    query = """
    CREATE (bb:Block {id: randomUUID(), block_name: $block_name, model_name: $model_name})
    RETURN bb.id AS id
    """
    result = await make_request(
        session=session,
        query=query,
        block_name=data.block_name,
    )
    record = await result.single()
    record_data = record.data()
    return BlockDataModel(**record_data)
