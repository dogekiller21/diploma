from fastapi import Depends, HTTPException, Request

from app.db.postgresql.models.dbuser import DBUser
from app.db.postgresql.session import AsyncPGSession
from app.exceptions.frontend import FrontendNotAuthException
from app.models.user import User, UserScopeEnum
from app.security.auth import decrypt_user_data


async def get_current_user(request: Request, session: AsyncPGSession) -> User:
    encrypted_user_data = request.session.get("user")
    if encrypted_user_data is None:
        raise FrontendNotAuthException(status_code=401, detail="Not authenticated")
    user_data = decrypt_user_data(encrypted_user_data)
    user = User.model_validate(user_data)
    if not await DBUser.check_user(
        session=session,
        username=user.username,
        hashed_password=user.hashed_password,
        scope=user.scope,
    ):
        raise FrontendNotAuthException(status_code=401, detail="Not authenticated")

    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.scope != UserScopeEnum.admin:
        raise FrontendNotAuthException(status_code=401, detail="Not authenticated")

    return user
