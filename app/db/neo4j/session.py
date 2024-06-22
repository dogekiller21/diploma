from typing import Any, Callable, Coroutine, TypeVar

from fastapi import Depends
from neo4j import AsyncGraphDatabase, AsyncSession

from app.config.db import DB_NAME, DB_PASSWORD, DB_USERNAME
from app.db.neo4j.base.storage import BaseStorage
from app.db.neo4j.misc import get_db_uri

driver = AsyncGraphDatabase.driver(uri=get_db_uri(), auth=(DB_USERNAME, DB_PASSWORD))


async def get_db_session():
    session = driver.session(database=DB_NAME)
    try:
        yield session
    finally:
        print("Closing session")
        await session.close()


async def execute_with_session(query: str, **kwargs) -> Any:
    async with driver.session(database=DB_NAME) as session:
        result = await session.run(query, **kwargs)
        return result


TClass = TypeVar("TClass", bound=BaseStorage)
TClassAny = TypeVar("TClassAny")
TReturn = Callable[[AsyncSession], Coroutine[Any, Any, TClass]]


def build_storage_dependency(storage_class: type[TClass]) -> TReturn:
    async def get_storage(session: AsyncSession = Depends(get_db_session)) -> TClass:
        return storage_class(session=session)

    return get_storage


def build_dispatcher_dependency(dispatcher_class: type[TClassAny]) -> TReturn:
    async def get_dispatcher(session: AsyncSession = Depends(get_db_session)):
        return dispatcher_class(session=session)

    return get_dispatcher
