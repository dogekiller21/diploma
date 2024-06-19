from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, datastructures
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.db.neo4j.block import BlockStorage
from app.db.neo4j.session import build_storage_dependency
from app.db.neo4j.version.storage import VersionStorage

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
async def all_firmwares_page(
    request: Request,
    car: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
):
    blocks = await storage.get_block_with_controllers_response(
        limit=100, offset=0, block_id=block
    )
    return templates.TemplateResponse(
        request=request,
        name="firmwares.html",
        context={
            "request": request,
            "title": "Поиск прошивок",
            "blocks": blocks,
        },
    )


@router.get(
    "/firmware/{firmware_id}",
    response_class=HTMLResponse,
    name="firmware",
    include_in_schema=False,
)
async def single_firmware_page(
    request: Request,
    firmware_id: str,
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
):
    firmware = await storage.get_controller_versions_response(
        limit=100, offset=0, controller_id=firmware_id
    )
    return templates.TemplateResponse(
        request=request,
        name="firmware.html",
        context={
            "request": request,
            "title": f"{firmware_id} - Прошивка",
            "firmware": firmware,
        },
    )


@router.get("/about", response_class=HTMLResponse, name="about_page")
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="main.html", context={"request": request}
    )
