import shutil
from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, datastructures
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from pydantic import BaseModel, Field, field_validator, model_validator, validator

from app.db.block.storage import BlockStorage
from app.db.controller.storage import ControllerStorage
from app.db.session import build_storage_dependency

router = APIRouter(prefix="")

templates = Jinja2Templates(directory="app/templates")


@pass_context
def https_url_for(context: dict, name: str, **path_params: Any) -> datastructures.URL:
    """
    https://stackoverflow.com/questions/70521784/fastapi-links-created-by-url-for-in-jinja2-template-use-http-instead-of-https

    """
    request = context.get("request")
    http_url = request.url_for(name, **path_params)

    # Replace 'http' with 'https'
    return http_url.replace(scheme="https")


templates.env.globals["https_url_for"] = https_url_for


class Firmware(BaseModel):
    id: int
    car: str
    block: str
    version: str
    release_date: date
    file: str


class Block(BaseModel):
    id: int
    name: str
    firmwares: list[Firmware]
    firmware_count: int | None = None

    @model_validator(mode="after")
    @classmethod
    def set_additional_info(cls, values):
        if values.firmware_count is None:
            values.firmware_count = len(values.firmwares)
        return values


class FirmwareResponse(BaseModel):
    success: bool
    message: str | None = None
    firmware: Firmware | None = None


firmwares_db = [
    Block(
        id=1,
        name="ECU",
        firmwares=[
            Firmware(
                id=1,
                car="Toyota Corolla",
                block="ECU",
                version="1.0.0",
                release_date=date(2022, 1, 1),
                file="firmware1.bin",
            ),
            Firmware(
                id=3,
                car="Ford Focus",
                block="ECU",
                version="1.2.0",
                release_date=date(2023, 3, 30),
                file="firmware3.bin",
            ),
        ],
    ),
    Block(
        id=2,
        name="TCU",
        firmwares=[
            Firmware(
                id=2,
                car="Honda Civic",
                block="TCU",
                version="1.1.0",
                release_date=date(2023, 2, 15),
                file="firmware2.bin",
            ),
        ],
    ),
    Block(
        id=3,
        name="BCM",
        firmwares=[
            Firmware(
                id=4,
                car="BMW 320i",
                block="BCM",
                version="2.0.0",
                release_date=date(2024, 4, 10),
                file="firmware4.bin",
            ),
        ],
    ),
]

firmware_versions = {
    1: [
        Firmware(
            id=1,
            car="Toyota Corolla",
            block="ECU",
            version="1.0.1",
            release_date=date(2022, 1, 1),
            file="firmware1.bin",
        ),
        Firmware(
            id=1,
            car="Toyota Corolla",
            block="ECU",
            version="1.0.0",
            release_date=date(2021, 1, 1),
            file="firmware2.bin",
        ),
        Firmware(
            id=1,
            car="Toyota Corolla",
            block="ECU",
            version="1.0.2",
            release_date=date(2023, 1, 1),
            file="firmware3.bin",
        ),
    ],
    2: [
        Firmware(
            id=2,
            car="Honda Civic",
            block="TCU",
            version="1.1.1",
            release_date=date(2021, 2, 15),
            file="firmware1.bin",
        ),
        Firmware(
            id=2,
            car="Honda Civic",
            block="TCU",
            version="2.1.0",
            release_date=date(2022, 2, 15),
            file="firmware2.bin",
        ),
        Firmware(
            id=2,
            car="Honda Civic",
            block="TCU",
            version="3.1.0",
            release_date=date(2023, 2, 15),
            file="firmware3.bin",
        ),
        Firmware(
            id=2,
            car="Honda Civic",
            block="TCU",
            version="4.2.3",
            release_date=date(2024, 2, 15),
            file="firmware4.bin",
        ),
    ],
    3: [
        Firmware(
            id=3,
            car="Ford Focus",
            block="ECU",
            version="1.2.0",
            release_date=date(2023, 3, 30),
            file="firmware1.bin",
        ),
        Firmware(
            id=3,
            car="Ford Focus",
            block="ECU",
            version="0.2.0",
            release_date=date(2022, 3, 30),
            file="firmware2.bin",
        ),
    ],
    4: [
        Firmware(
            id=4,
            car="BMW 320i",
            block="BCM",
            version="1.0.0",
            release_date=date(2021, 4, 10),
            file="firmware1.bin",
        ),
        Firmware(
            id=4,
            car="BMW 320i",
            block="BCM",
            version="0.0.1",
            release_date=date(2020, 4, 10),
            file="firmware2.bin",
        ),
        Firmware(
            id=4,
            car="BMW 320i",
            block="BCM",
            version="2.0.0",
            release_date=date(2022, 4, 10),
            file="firmware3.bin",
        ),
        Firmware(
            id=4,
            car="BMW 320i",
            block="BCM",
            version="3.0.0",
            release_date=date(2023, 4, 10),
            file="firmware4.bin",
        ),
        Firmware(
            id=4,
            car="BMW 320i",
            block="BCM",
            version="4.0.1",
            release_date=date(2024, 4, 10),
            file="firmware5.bin",
        ),
    ],
}


@router.get("/", response_class=HTMLResponse, name="main_page", include_in_schema=False)
async def main_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={"request": request, "title": "Главная страница"},
    )


@router.get(
    "/firmwares",
    response_class=HTMLResponse,
    name="firmwares_page",
    include_in_schema=False,
)
async def firmwares_page(
    request: Request,
    car: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
):
    firmwares = await storage.get_block_with_controllers_response(
        limit=100, offset=0, block_id=block
    )
    return templates.TemplateResponse(
        request=request,
        name="firmwares.html",
        context={
            "request": request,
            "title": "Поиск прошивок",
            "blocks": firmwares,
        },
    )


@router.get(
    "/firmware/{firmware_id}",
    response_class=HTMLResponse,
    name="firmware",
    include_in_schema=False,
)
async def firmwares_page(
    request: Request,
    firmware_id: int,
):
    versions = sorted(
        firmware_versions[firmware_id], key=lambda x: x.release_date, reverse=True
    )
    return templates.TemplateResponse(
        request=request,
        name="firmware.html",
        context={
            "request": request,
            "title": f"{firmware_id} - Прошивка",
            "versions": versions,
        },
    )


@router.post("/add_firmware", name="add_firmware")
async def add_firmware(
    car: Annotated[str, Form(...)],
    block: Annotated[str, Form(...)],
    version: Annotated[str, Form(...)],
    release_date: Annotated[date, Form(...)],
    file: UploadFile = File(...),
) -> FirmwareResponse:
    new_id = len(firmwares_db) + 1

    file_location = f"app/static/firmwares/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_firmware = Firmware(
        id=new_id,
        car=car,
        block=block,
        version=version,
        release_date=release_date,
        file=file.filename,
    )
    firmwares_db.append(new_firmware)
    return FirmwareResponse(success=True, firmware=new_firmware)


@router.get("/about", response_class=HTMLResponse, name="about_page")
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="main.html", context={"request": request}
    )
