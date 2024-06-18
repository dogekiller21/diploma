import io
import json
import logging
import mimetypes
from typing import Annotated
from uuid import UUID

import magic
from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.params import Body, File, Form, Path, Query
from fastapi.responses import StreamingResponse

from app.db.block.storage import BlockStorage
from app.db.car.storage import CarStorage
from app.db.controller.storage import ControllerStorage
from app.db.links.dispatcher import LinkDispatcher
from app.db.links.storage import LinkStorage
from app.db.session import build_dispatcher_dependency, build_storage_dependency
from app.db.version.storage import VersionStorage
from app.models.block import (
    BlockCreateModel,
    BlockDataModel,
    BlockDeleteModel,
    ModalBlockCreateModel,
)
from app.models.car import CarCreateModel, CarDataModel
from app.models.controller import ControllerCreateModel, ControllerDataModel
from app.models.response import (
    BlockControllerResponseModel,
    BlockControllersResponseModel,
    FirmwareResponse,
    FirmwareVersionResponse,
)
from app.models.versions import VersionCreateModel, VersionDataModel

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/crud")


@router.post("/add_firmware", name="add_firmware")
async def add_firmware(
    controller: str = Form(...),
    block: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> FirmwareResponse:
    controller = ControllerCreateModel.model_validate(json.loads(controller))
    block = ModalBlockCreateModel.model_validate(json.loads(block))
    version = VersionCreateModel.model_validate(json.loads(version))
    version.data = await file.read()
    return await storage.create_controller_block_full(
        controller=controller,
        block=block,
        version=version,
    )


@router.post("/car")
async def create_car(
    data: CarCreateModel,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel:
    return await storage.create_car_object(data=data)


@router.post("/block")
async def create_block(
    data: BlockCreateModel,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> BlockDataModel:
    return await storage.create_block_object(data=data)


@router.post("/version")
async def create_version(
    data: VersionCreateModel,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
) -> VersionDataModel:
    return await storage.create_version_object(data=data)


@router.post("/controller")
async def create_controller(
    data: ControllerCreateModel,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> ControllerDataModel:
    return await storage.create_controller_object(data=data)


@router.post("/link_controller")
async def link_controller_to_block(
    controller_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_controller_to_block(
        controller_id=controller_id,
        block_id=block_id,
    )


@router.post("/link_car")
async def link_car(
    car_id: str,
    block_id: str,
    dispatcher: LinkDispatcher = Depends(build_dispatcher_dependency(LinkDispatcher)),
) -> None:
    return await dispatcher.link_car_to_block(car_id=car_id, block_id=block_id)


@router.get("/block_controllers")
async def get_block_controllers(
    block_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_block_linked_controllers(block_id=block_id)


@router.get("/car_controllers")
async def get_car_controllers(
    car_id: str,
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> list[ControllerDataModel]:
    return await storage.get_car_linked_controllers(car_id=car_id)


@router.get("/car")
async def get_car_by_numberplate(
    numberplate: str,
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> CarDataModel | None:
    return await storage.get_car_object_by_numberplate(numberplate=numberplate)


@router.get("/controller_data")
async def get_controller_data(
    controller_id: str,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> list[bytes] | None:
    return await storage.get_controller_data(controller_id=controller_id)


@router.get("/controllers")
async def get_controller(
    offset: int = 0,
    limit: int = 5,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> list[BlockControllerResponseModel]:
    return await storage.get_controllers_response(limit=limit, offset=offset)


@router.get("/blocks_full", name="get_blocks_full")
async def get_blocks_full(
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> list[BlockControllersResponseModel]:
    return await storage.get_block_with_controllers_response(
        limit=100,
        offset=0,
    )


@router.delete("/block", name="delete_block")
async def delete_block_by_id(
    block_data: BlockDeleteModel,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> int:
    return await storage.delete_block_by_id(block_id=str(block_data.id))


@router.get("/blocks", name="get_blocks")
async def get_blocks(
    offset: int = 0,
    limit: int = 5,
    query: str = None,
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
) -> list[BlockDataModel]:
    return await storage.get_blocks_response(limit=limit, offset=offset, query=query)


@router.get("/download_firmware/{version_id}", name="download_firmware")
async def download_firmware_response(
    version_id: str,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
) -> StreamingResponse:
    version_data = await storage.get_version_data(version_id=version_id)
    mime_type = magic.from_buffer(version_data.data[:2048], mime=True)
    file_extension = mimetypes.guess_extension(type=mime_type, strict=False)
    if file_extension is None:
        file_extension = ".bin"
    buffer = io.BytesIO(version_data.data)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type=mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={version_id}{file_extension}"
        },
    )


@router.post("/firmware_version", name="add_firmware_version")
async def add_firmware_version(
    firmware_id: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> FirmwareVersionResponse:
    version = VersionCreateModel.model_validate(json.loads(version))
    version.data = await file.read()
    return await storage.create_firmware_version(
        firmware_id=firmware_id,
        version=version,
    )


@router.delete("/car")
async def delete_car_by_id(
    internal_id: Annotated[str, Query(alias="id")],
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
) -> int:
    return await storage.delete_car_object_by_id(internal_id=internal_id)
