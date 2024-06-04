from app.db.base.storage import BaseStorage
from app.models.block import BlockCreateModel, BlockDataModel


class BlockStorage(BaseStorage):
    async def create_block_object(
        self,
        data: BlockCreateModel,
    ) -> BlockDataModel:
        query = """
        CREATE (bb:Block {id: randomUUID(), block_name: $block_name, model_name: $model_name})
        RETURN bb.id AS id
        """
        result = await self.make_request(
            query=query,
            block_name=data.block_name,
        )
        record = await result.single()
        record_data = record.data()
        return BlockDataModel(**record_data)
