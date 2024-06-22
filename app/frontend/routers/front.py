from typing import Any, Optional

from fastapi import APIRouter, Depends, Form, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.db.neo4j.block.storage import BlockStorage
from app.db.neo4j.car.storage import CarStorage
from app.db.neo4j.session import build_storage_dependency
from app.db.neo4j.version.storage import VersionStorage
from app.db.postgresql.models.dbuser import DBUser
from app.db.postgresql.session import AsyncPGSession
from app.dependencies.auth import get_admin_user_front, get_current_user_front
from app.frontend.misc import templates
from app.models.user import User, UserScopeEnum
from app.security.auth import decrypt_user_data, encrypt_user_data, get_password_hash
from app.services.auth import auth_user, register_user

router = APIRouter(prefix="")


@router.get("/", response_class=HTMLResponse, name="main_page", include_in_schema=False)
async def main_page(request: Request, user: User = Depends(get_current_user_front)):
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={"request": request, "title": "Главная страница", "user": user},
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
    user: User = Depends(get_current_user_front),
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
):
    blocks = await storage.get_block_with_controllers_response(
        limit=100, offset=0, block_id=block, car_id=car
    )
    return templates.TemplateResponse(
        request=request,
        name="firmwares.html",
        context={
            "request": request,
            "title": "Поиск прошивок",
            "blocks": blocks,
            "user": user,
        },
    )


@router.get(
    "/cars",
    response_class=HTMLResponse,
    name="cars_page",
    include_in_schema=False,
)
async def all_cars_page(
    request: Request,
    car: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    user: User = Depends(get_current_user_front),
    storage: CarStorage = Depends(build_storage_dependency(CarStorage)),
):
    cars = await storage.get_cars_with_blocks_response(
        limit=100, offset=0, block_id=block, car_id=car
    )
    return templates.TemplateResponse(
        request=request,
        name="cars.html",
        context={
            "request": request,
            "title": "Просмотр автомобилей",
            "cars": cars,
            "user": user,
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
    user: User = Depends(get_current_user_front),
    storage: VersionStorage = Depends(build_storage_dependency(VersionStorage)),
):
    firmware = await storage.get_controller_versions_response(
        limit=100, offset=0, controller_id=firmware_id
    )
    if not firmware:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"request": request}
        )
    return templates.TemplateResponse(
        request=request,
        name="firmware.html",
        context={
            "request": request,
            "title": f"{firmware_id} - Прошивка",
            "firmware": firmware,
            "user": user,
        },
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
    name="register",
    include_in_schema=False,
)
async def register_form(request: Request, user: User = Depends(get_admin_user_front)):
    return templates.TemplateResponse(
        "register.html", {"request": request, "user": user}
    )


@router.post(
    "/register",
    include_in_schema=False,
)
async def register(
    request: Request,
    session: AsyncPGSession,
    username: str = Form(...),
    password: str = Form(...),
    scope: UserScopeEnum = Form(UserScopeEnum.user),
):
    if await DBUser.exists(session=session, username=username):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Пользователь с таким именем уже существует"},
        )
    user = await register_user(
        session=session, username=username, password=password, scope=scope
    )
    request.session["user"] = encrypt_user_data(user.dict())
    return RedirectResponse(url="/", status_code=302)


@router.get(
    "/login",
    response_class=HTMLResponse,
    name="login",
    include_in_schema=False,
)
async def login_form(request: Request, user: User = Depends(get_current_user_front)):
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "Авторизация", "user": user}
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def login(
    request: Request,
    session: AsyncPGSession,
    username: str = Form(...),
    password: str = Form(...),
):
    user = await auth_user(session=session, username=username, password=password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный данные для авторизации"},
        )
    request.session["user"] = encrypt_user_data(user.dict())
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get(
    "/logout",
    name="logout",
    include_in_schema=False,
)
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=302)


@router.get(
    "/block/{block_id}",
    response_class=HTMLResponse,
    name="block_page",
    include_in_schema=False,
)
async def single_block_page(
    request: Request,
    block_id: str,
    user: User = Depends(get_current_user_front),
    storage: BlockStorage = Depends(build_storage_dependency(BlockStorage)),
):
    blocks = await storage.get_block_with_controllers_response(
        limit=1, offset=0, block_id=block_id
    )
    if not blocks:
        return templates.TemplateResponse(
            request=request, name="404.html", context={"request": request, "user": user}
        )
    block = blocks[0]
    return templates.TemplateResponse(
        request=request,
        name="block.html",
        context={
            "request": request,
            "title": f"{block_id} - Блок",
            "block": block,
            "user": user,
        },
    )


@router.get(
    "/about", response_class=HTMLResponse, name="about_page", include_in_schema=False
)
async def about_page(request: Request, user: User = Depends(get_current_user_front)):
    return templates.TemplateResponse(
        request=request,
        name="contacts.html",
        context={"request": request, "title": "Контакты", "user": user},
    )
