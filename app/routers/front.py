import shutil
from datetime import date
from typing import Optional, Annotated

from fastapi import APIRouter, Query, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel, validator, field_validator, Field, model_validator

router = APIRouter(prefix="")

templates = Jinja2Templates(directory="app/templates")


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
):
    return templates.TemplateResponse(
        request=request,
        name="firmwares.html",
        context={
            "request": request,
            "title": "Поиск прошивок",
            "blocks": firmwares_db,
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
