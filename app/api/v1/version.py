import io
import json
import mimetypes

import magic
from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File, Form
from fastapi.responses import StreamingResponse

from app.db.neo4j.links.storage import LinkStorage
from app.db.neo4j.session import build_storage_dependency
from app.db.neo4j.version.storage import VersionStorage
from app.models.controller import SingleControllerDataModel
from app.models.response import FirmwareVersionAPIResponse
from app.models.versions import VersionCreateModel, VersionDataModel, VersionDeleteModel

router = APIRouter(prefix="/version", tags=["version"])


@router.get("/download/{version_id}", name="download_firmware")
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


@router.post("/")
async def create_version(
    data: VersionCreateModel,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
) -> VersionDataModel:
    return await storage.create_version_object(data=data)


@router.post("/firmware", name="add_firmware_version")
async def add_firmware_version(
    firmware_id: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
    storage: LinkStorage = Depends(build_storage_dependency(LinkStorage)),
) -> FirmwareVersionAPIResponse:
    version = VersionCreateModel.model_validate(json.loads(version))
    version.data = await file.read()
    return await storage.create_firmware_version(
        firmware_id=firmware_id,
        version=version,
    )


@router.delete("/", name="delete_version")
async def delete_version(
    data: VersionDeleteModel,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
) -> int:
    data = await storage.delete_version_by_id(version_id=str(data.id))
    print(f"{data=}")
    return data


@router.get("/firmware", name="get_firmware_versions")
async def get_firmware_versions(
    firmware_id: str,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
) -> SingleControllerDataModel | None:
    return await storage.get_controller_versions_response(
        limit=100, offset=0, controller_id=firmware_id
    )
