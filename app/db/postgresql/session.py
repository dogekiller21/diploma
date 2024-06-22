import logging
from typing import Annotated, Any, AsyncIterator

from fastapi import Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.postgresql.misc import get_db_uri

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    get_db_uri(),
    pool_pre_ping=True,
    echo=False,
)

sync_engine = create_engine(
    get_db_uri(),
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    future=True,
)


async def get_postgres_session() -> AsyncIterator[AsyncSession]:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        await session.close()


AsyncPGSession = Annotated[AsyncSession, Depends(get_postgres_session)]


async def execute_with_session(smtm, **kwargs) -> Any:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(smtm, kwargs)
            return result
    except Exception as e:
        logger.exception(e)
    finally:
        await session.close()
