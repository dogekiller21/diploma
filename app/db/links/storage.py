import logging

from neo4j import AsyncTransaction

from app.db.base.storage import BaseStorage
from app.db.block.storage import BlockStorage
from app.db.controller.storage import ControllerStorage
from app.db.links.dispatcher import LinkDispatcher
from app.db.version.storage import VersionStorage
from app.models.block import BlockCreateModel, ModalBlockCreateModel
from app.models.controller import (
    ControllerCreateModel,
    ControllerDataModel,
    SingleBlockControllerResponseModel,
)
from app.models.response import FirmwareResponse, FirmwareVersionResponse
from app.models.versions import VersionCreateModel, VersionResponseModel

logger = logging.getLogger(__name__)


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
        return [ControllerDataModel.model_validate(item.get("cc")) for item in data]

    async def get_car_linked_controllers(
        self,
        car_id: str,
    ) -> list[ControllerDataModel]:
        query = """
            MATCH (cc:Controller)-[:LINKED_BLOCK]->(blocks:Block)<-[:LINKED_CAR]--(cars:Car)
            WHERE cars.id = $car_id
            return cc
        """

        result = await self.make_request(
            query=query,
            car_id=car_id,
        )
        data = await result.data()
        if not data:
            return []
        return [ControllerDataModel.model_validate(item.get("cc")) for item in data]

    async def create_controller_block_full(
        self,
        controller: ControllerCreateModel,
        block: ModalBlockCreateModel,
        version: VersionCreateModel,
    ) -> FirmwareResponse:
        async with await self.session.begin_transaction() as tx:
            try:
                controller_storage = ControllerStorage(session=tx)
                block_storage = BlockStorage(session=tx)
                version_storage = VersionStorage(session=tx)
                dispatcher = LinkDispatcher(session=tx)

                new_controller = await controller_storage.create_controller_object(
                    controller
                )
                if block.id is None:
                    new_block = await block_storage.create_block_object(block)
                else:
                    new_block = await block_storage.get_block_by_id(block_id=block.id)

                if new_block is None:
                    return FirmwareResponse(
                        success=False, message="Cant find corresponding block"
                    )

                new_version = await version_storage.create_version_object(version)
                await dispatcher.link_controller_to_block(
                    controller_id=str(new_controller.id), block_id=str(new_block.id)
                )
                await dispatcher.link_version_to_controller(
                    controller_id=str(new_controller.id), version_id=str(new_version.id)
                )

                response_dict = new_controller.dict()
                response_dict["block"] = new_block.dict()
                response_dict["first_version"] = new_version.dict()
                response_dict["versions"] = [new_version.dict()]
                response = SingleBlockControllerResponseModel.model_validate(
                    response_dict
                )

            except Exception as e:
                logger.error("Error creating full controller: %s", e, exc_info=e)
                await tx.rollback()
                return FirmwareResponse(
                    success=False, message="Error creating full controller"
                )
            else:
                await tx.commit()
                return FirmwareResponse(success=True, firmware=response)

    async def create_firmware_version(
        self, firmware_id: str, version: VersionCreateModel
    ) -> FirmwareVersionResponse:
        async with await self.session.begin_transaction() as tx:
            try:
                version_storage = VersionStorage(session=tx)
                new_version = await version_storage.create_version_object(version)
                dispatcher = LinkDispatcher(session=tx)
                await dispatcher.link_version_to_controller(
                    version_id=str(new_version.id), controller_id=firmware_id
                )
                version_response_model = VersionResponseModel.model_validate(
                    new_version.dict()
                )
            except Exception as e:
                logger.error("Error creating firmware version: %s", e, exc_info=e)
                await tx.rollback()
                return FirmwareVersionResponse(
                    success=False, message="Error creating version"
                )
            else:
                await tx.commit()
                return FirmwareVersionResponse(
                    success=True, version=version_response_model
                )
