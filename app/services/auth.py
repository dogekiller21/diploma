from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgresql.models.dbuser import DBUser
from app.models.user import User, UserScopeEnum
from app.security.auth import get_password_hash, verify_password


async def auth_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await DBUser.get_by_username(session, username)
    if user is None:
        return None
    if not verify_password(
        plain_password=password, hashed_password=user.hashed_password
    ):
        return None
    return User.model_validate(user)


async def register_user(
    session: AsyncSession, username: str, password: str, scope: UserScopeEnum
) -> User | None:
    user = await DBUser.create(
        session=session,
        username=username,
        hashed_password=get_password_hash(password),
        scope=scope,
    )
    return User.model_validate(user)
