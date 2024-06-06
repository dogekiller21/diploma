from app.db.base.storage import BaseStorage
from app.models.block import BlockCreateModel, BlockDataModel


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
