from neo4j import AsyncSession

from app.db.crud.requests import make_request
from app.models.car import BlockCreateModel, BlockDataModel


async def create_block_object(
    data: BlockCreateModel, session: AsyncSession
) -> BlockDataModel:
    result = await make_request(
        session=session,
        query="CREATE (bb:Block {id: randomUUID(), block_name: $block_name, data: $data}) RETURN bb.id AS id",
        block_name=data.block_name,
        data=data.data,
    )
    record = await result.single()
    record_data = record.data()
    record_data.update(data.dict())
    return BlockDataModel(**record_data)
