import asyncio

from neo4j import AsyncResult, AsyncSession


async def make_request(query: str, session: AsyncSession, **kwargs) -> AsyncResult:
    try:
        result: AsyncResult = await session.run(query=query, **kwargs)
    except asyncio.CancelledError:
        session.cancel()
        raise
    else:
        return result
