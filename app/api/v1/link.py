import json
import logging

from fastapi import APIRouter, Depends, Form, Request

from app.db.neo4j.links.dispatcher import LinkDispatcher
from app.db.neo4j.links.storage import LinkStorage
from app.db.neo4j.session import build_dispatcher_dependency, build_storage_dependency
from app.dependencies.auth import get_admin_user, get_admin_user_front
from app.models.block import ModalBlockCreateModel
from app.models.link import CarBlockLinkModel, CarBlockUnLinkModel
from app.models.response import BaseAPIResponse
from app.models.user import User

router = APIRouter(prefix="/link", tags=["link"])


logger = logging.getLogger(__name__)


@router.post("/firmware_block", dependencies=[Depends(get_admin_user)])
async def link_firmware_to_block(
    controller_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_controller_to_block(
        controller_id=controller_id,
        block_id=block_id,
    )


@router.delete(
    "/car_block",
    name="unlink_block_to_car",
    dependencies=[Depends(get_admin_user)],
)
async def unlink_car_to_block(
    data: CarBlockUnLinkModel,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> int:
    try:
        return await dispatcher.unlink_block_to_car(
            car_id=data.car_id, block_id=data.block_id
        )
    except Exception as e:
        logger.error("Error unlinking car from block: %s", e, exc_info=e)
        return 0


@router.post(
    "/car_block", name="link_block_to_car", dependencies=[Depends(get_admin_user)]
)
async def link_car_to_block(
    data: CarBlockLinkModel,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> BaseAPIResponse:
    try:
        return await storage.link_car_block_full(car_id=data.car_id, block=data.block)
    except Exception as e:
        logger.error("Error linking car to block: %s", e, exc_info=e)
        return BaseAPIResponse(success=False, message="Произошла серверная ошибка")
