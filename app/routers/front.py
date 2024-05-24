import shutil
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import urllib.parse

router = APIRouter(prefix="")

templates = Jinja2Templates(directory="app/templates")


class Firmware(BaseModel):
    id: int
    car: str
    block: str
    version: str
    release_date: date
    file: str


firmwares_db = [
    Firmware(
        id=1,
        car="Toyota Corolla",
        block="ECU",
        version="1.0.0",
        release_date=date(2022, 1, 1),
        file="firmware1.bin",
    ),
    Firmware(
        id=2,
        car="Honda Civic",
        block="TCU",
        version="1.1.0",
        release_date=date(2023, 2, 15),
        file="firmware2.bin",
    ),
    Firmware(
        id=3,
        car="Ford Focus",
        block="ECU",
        version="1.2.0",
        release_date=date(2023, 3, 30),
        file="firmware3.bin",
    ),
    Firmware(
        id=4,
        car="BMW 320i",
        block="BCM",
        version="2.0.0",
        release_date=date(2024, 4, 10),
        file="firmware4.bin",
    ),
]


@router.get("/", response_class=HTMLResponse, name="main_page")
async def main_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={"request": request, "title": "Главная страница"},
    )


@router.get("/firmwares", response_class=HTMLResponse, name="firmwares_page")
async def firmwares_page(
    request: Request,
    car: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
):
    filtered_firmwares = [
        fw
        for fw in firmwares_db
        if (car.lower() in fw.car.lower() if car else True)
        and (block.lower() in fw.block.lower() if block else True)
    ]
    return templates.TemplateResponse(
        request=request,
        name="firmwares.html",
        context={
            "request": request,
            "title": "Поиск прошивок",
            "firmwares": filtered_firmwares,
        },
    )


@router.post("/add_firmware", response_class=HTMLResponse, name="add_firmware")
async def add_firmware(
    request: Request,
    car: str = Form(...),
    block: str = Form(...),
    version: str = Form(...),
    release_date: date = Form(...),
    file: UploadFile = File(...),
    car_query: Optional[str] = Form(None),
    block_query: Optional[str] = Form(None),
):
    new_id = len(firmwares_db) + 1

    file_location = f"static/firmwares/{file.filename}"
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
    query_params = {}
    if car_query:
        query_params["car"] = car_query
    if block_query:
        query_params["block"] = block_query
    query_string = urllib.parse.urlencode(query_params)
    return RedirectResponse(url=f"/firmwares?{query_string}", status_code=303)


@router.get("/about", response_class=HTMLResponse, name="about_page")
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="main.html", context={"request": request}
    )
