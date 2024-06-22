from fastapi import APIRouter, Depends, HTTPException

from app.db.neo4j.block.storage import BlockStorage
from app.db.neo4j.links.storage import LinkStorage
from app.db.neo4j.session import build_storage_dependency
from app.dependencies.auth import get_admin_user, get_current_user
from app.models.block import BlockCreateModel, BlockDataModel, BlockDeleteModel
from app.models.controller import ControllerDataModel
from app.models.response import BlockControllersResponseModel

router = APIRouter(prefix="/block", tags=["block"])


@router.post("/", dependencies=[Depends(get_admin_user)])
async def create_block(
    data: BlockCreateModel,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> BlockDataModel:
    return await storage.create_block_object(data=data)


@router.get("/firmware", dependencies=[Depends(get_current_user)])
async def get_block_firmware(
    block_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_block_linked_controllers(block_id=block_id)


@router.get("/full", name="get_blocks_full", dependencies=[Depends(get_current_user)])
async def get_blocks_full(
    block: str | None = None,
    car: str | None = None,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> list[BlockControllersResponseModel]:
    return await storage.get_block_with_controllers_response(
        limit=100,
        offset=0,
    )


@router.get(
    "/single_full",
    name="get_single_block_full",
    dependencies=[Depends(get_current_user)],
)
async def get_single_block_full(
    block_id: str,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> BlockControllersResponseModel:
    blocks = await storage.get_block_with_controllers_response(
        limit=1,
        offset=0,
        block_id=block_id,
    )
    if not blocks:
        raise HTTPException(status_code=404, detail="Block not found")
    return blocks[0]


@router.delete("/", name="delete_block", dependencies=[Depends(get_admin_user)])
async def delete_block_by_id(
    block_data: BlockDeleteModel,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> int:
    return await storage.delete_block_by_id(block_id=str(block_data.id))


@router.get("/", name="get_blocks", dependencies=[Depends(get_current_user)])
async def get_blocks(
    offset: int = 0,
    limit: int = 5,
    query: str = None,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> list[BlockDataModel]:
    return await storage.get_blocks_response(limit=limit, offset=offset, query=query)
