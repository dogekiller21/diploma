from app.db.base.storage import BaseStorage
from app.db.block.storage import BlockStorage
from app.db.controller.storage import ControllerStorage
from app.db.links.dispatcher import LinkDispatcher
from app.models.block import BlockCreateModel
from app.models.controller import ControllerCreateModel, ControllerDataModel


class LinkStorage(BaseStorage):
    async def get_block_linked_controllers(
        self,
        block_id: str,
    ) -> list[ControllerDataModel]:
        query = "MATCH (cc:Controller)-[:LINKED_BLOCK]->(blocks:Block) WHERE blocks.id = $block_id return cc"

        result = await self.make_request(
            query=query,
            block_id=block_id,
        )
        data = await result.data()
        if not data:
            return []
        return [ControllerDataModel(**item.get("cc")) for item in data]

    async def get_car_linked_controllers(
        self,
        car_id: str,
    ) -> list[ControllerDataModel]:
        query = "MATCH (cc:Controller)-[:LINKED_CAR]->(cars:Car) WHERE cars.id = $car_id return cc"

        result = await self.make_request(
            query=query,
            car_id=car_id,
        )
        data = await result.data()
        if not data:
            return []
        return [ControllerDataModel(**item.get("cc")) for item in data]

    async def create_controller_block_full(
        self, controller: ControllerCreateModel, block: BlockCreateModel
    ):
        controller_storage = ControllerStorage(self.session)
        block_storage = BlockStorage(self.session)
        dispatcher = LinkDispatcher(self.session)

        new_controller = await controller_storage.create_controller_object(controller)
        new_block = await block_storage.create_block_object(block)

        await dispatcher.link_controller_to_block(
            controller_id=str(new_controller.id), block_id=str(new_block.id)
        )

        return new_controller
