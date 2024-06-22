from fastapi import APIRouter

from app.db.postgresql.models.dbuser import DBUser
from app.db.postgresql.session import AsyncPGSession
from app.models.user import UserScopeEnum

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/test")
async def test_route(session: AsyncPGSession):
    await DBUser.create(
        session, username="test", hashed_password="test", scope=UserScopeEnum.user
    )
