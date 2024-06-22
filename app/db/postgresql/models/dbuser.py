from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgresql.models.base import Base
from app.models.user import UserScopeEnum
from app.security.auth import get_password_hash, verify_password


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    username: Mapped[str] = mapped_column("username", String(length=64), nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        "hashed_password", String(length=1024), nullable=False
    )
    scope: Mapped[UserScopeEnum] = mapped_column(
        "scope", String(length=16), nullable=False
    )

    @classmethod
    async def create_admin_if_not_exists(
        cls, session: AsyncSession | AsyncConnection, password: str
    ):
        user = await cls.get_by_username(session, "admin")
        if user is None:
            await cls.create(
                session=session,
                username="admin",
                hashed_password=get_password_hash(password),
                scope=UserScopeEnum.admin,
            )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        username: str,
        hashed_password: str,
        scope: UserScopeEnum,
    ):
        user = DBUser(username=username, hashed_password=hashed_password, scope=scope)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str):
        stmt = select(cls).where(cls.username == username)
        return await session.scalar(stmt)

    @classmethod
    async def check_user(
        cls,
        session: AsyncSession,
        username: str,
        hashed_password: str,
        scope: UserScopeEnum,
    ):
        user = await cls.get_by_username(session, username)
        if user.scope != scope:
            return False
        if user.hashed_password != hashed_password:
            return False
        return True

    @classmethod
    async def exists(cls, username: str, session: AsyncSession):
        user = await cls.get_by_username(session, username)
        return user is not None
