from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.db.postgresql.models.dbuser import DBUser
from app.db.postgresql.session import AsyncPGSession
from app.exceptions.frontend import FrontendNotAuthException
from app.models.user import User, UserScopeEnum
from app.security.auth import decrypt_user_data


def _build_get_current_user(raise_exp: Exception):
    async def func(request: Request, session: AsyncPGSession) -> User:
        encrypted_user_data = request.session.get("user")
        if encrypted_user_data is None:
            raise raise_exp
        user_data = decrypt_user_data(encrypted_user_data)
        user = User.model_validate(user_data)
        if not await DBUser.check_user(
            session=session,
            username=user.username,
            hashed_password=user.hashed_password,
            scope=user.scope,
        ):
            raise raise_exp

        return user

    return func


async def get_current_user_front(request: Request, session: AsyncPGSession) -> User:
    return await _build_get_current_user(
        raise_exp=FrontendNotAuthException(status_code=401, detail="Не авторизован")
    )(request=request, session=session)


def _build_get_admin_user(raise_exp: Exception):
    async def func(user: User) -> User:
        if user.scope != UserScopeEnum.admin:
            raise raise_exp

        return user

    return func


async def get_admin_user_front(
    user: Annotated[
        User,
        Depends(get_current_user_front),
    ]
) -> User:
    return await _build_get_admin_user(
        raise_exp=FrontendNotAuthException(status_code=401, detail="Не авторизован")
    )(user=user)


async def get_current_user(
    user: Annotated[
        User,
        Depends(
            _build_get_current_user(
                raise_exp=HTTPException(status_code=401, detail="Не авторизован")
            )
        ),
    ]
) -> User:
    return user


async def get_admin_user(
    user: Annotated[
        User,
        Depends(get_current_user),
    ]
) -> User:
    return await _build_get_admin_user(
        raise_exp=HTTPException(
            status_code=401, detail="У вас нет прав на выполнение этой операции"
        )
    )(user=user)
