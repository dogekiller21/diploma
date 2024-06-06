from typing import Any, Coroutine, TypeVar

from fastapi import Depends
from neo4j import AsyncGraphDatabase, AsyncSession

from app.config.db import DB_NAME, DB_PASSWORD, DB_USERNAME
from app.db.base.storage import BaseStorage
from app.db.misc import get_db_uri

driver = AsyncGraphDatabase.driver(uri=get_db_uri(), auth=(DB_USERNAME, DB_PASSWORD))


async def get_db_session():
    session = driver.session(database=DB_NAME)
    try:
        yield session
    finally:
        await session.close()


TClass = TypeVar("TClass", bound=BaseStorage)
TClassAny = TypeVar("TClassAny")
TReturn = (Coroutine[Any, Any, TClass],)


def build_storage_dependency(storage_class: type[TClass]) -> TReturn:
    async def get_storage(session: AsyncSession = Depends(get_db_session)):
        return storage_class(session=session)

    return get_storage


def build_dispatcher_dependency(dispatcher_class: type[TClassAny]) -> TReturn:
    async def get_dispatcher(session: AsyncSession = Depends(get_db_session)):
        return dispatcher_class(session=session)

    return get_dispatcher
