from fastapi import HTTPException, Request

from app.frontend.misc import templates


async def frontend_not_auth_exception_handler(
    request: Request, exception: HTTPException
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "title": "Авторизация"},
    )
