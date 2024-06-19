import json

from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File, Form

from app.db.neo4j.controller import ControllerStorage
from app.db.neo4j.links import LinkStorage
from app.db.neo4j.session import build_storage_dependency
from app.models.block import ModalBlockCreateModel
from app.models.controller import (
    BlockControllerResponseModel,
    ControllerCreateModel,
    ControllerDataModel,
    ControllerDeleteModel,
)
from app.models.response import FirmwareAPIResponse
from app.models.versions import VersionCreateModel

router = APIRouter(prefix="/firmware", tags=["firmware"])


@router.post("/full", name="add_firmware")
async def add_firmware(
    controller: str = Form(...),
    block: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> FirmwareAPIResponse:
    controller = ControllerCreateModel.model_validate(json.loads(controller))
    block = ModalBlockCreateModel.model_validate(json.loads(block))
    version = VersionCreateModel.model_validate(json.loads(version))
    version.data = await file.read()
    return await storage.create_controller_block_full(
        controller=controller,
        block=block,
        version=version,
    )


@router.post("/")
async def create_firmware(
    data: ControllerCreateModel,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> ControllerDataModel:
    return await storage.create_controller_object(data=data)


@router.get("/")
async def get_firmware(
    offset: int = 0,
    limit: int = 5,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> list[BlockControllerResponseModel]:
    return await storage.get_controllers_response(limit=limit, offset=offset)


@router.delete("/", name="delete_firmware")
async def delete_firmware(
    data: ControllerDeleteModel,
    storage: ControllerStorage = Depends(build_storage_dependency(ControllerStorage)),
) -> int:
    return await storage.delete_firmware_by_id(firmware_id=str(data.id))
