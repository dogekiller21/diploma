from app.db.base.storage import BaseStorage
from app.models.controller import ControllerCreateModel, ControllerDataModel


class ControllerStorage(BaseStorage):
    async def create_controller_object(
        self,
        data: ControllerCreateModel,
    ) -> ControllerDataModel:
        query = """
        CREATE
        (cc:Controller {id: randomUUID(), controller_name: $controller_name, data: $data})
        RETURN cc.id AS id
        """
        result = await self.make_request(
            query=query,
            controller_name=data.controller_name,
            data=data.data,
        )
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        return ControllerDataModel(**record_data)

    async def get_controller_block_data(self, controller_id: str) -> list[bytes] | None:
        result = await self.make_request(
            query="MATCH (cc:Controller) WHERE cc.id = $controller_id RETURN cc.data as data",
            controller_id=controller_id,
        )
        data = await result.data()
        if not data:
            return None
        return data[0]["data"]
