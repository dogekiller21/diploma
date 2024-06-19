from fastapi import APIRouter, Depends

from app.db.neo4j.links import LinkDispatcher
from app.db.neo4j.session import build_dispatcher_dependency

router = APIRouter(prefix="/link", tags=["link"])


@router.post("/firmware_block")
async def link_firmware_to_block(
    controller_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_controller_to_block(
        controller_id=controller_id,
        block_id=block_id,
    )


@router.post("/car_block")
async def link_car(
    car_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_car_to_block(car_id=car_id, block_id=block_id)
