from uuid import UUID

from app.db.base.storage import BaseStorage
from app.models.controller import ControllerDataModel


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
