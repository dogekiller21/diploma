import asyncio
from abc import ABC

from neo4j import AsyncResult, AsyncSession, AsyncTransaction


class BaseStorage(ABC):
    """
    https://habr.com/ru/companies/otus/articles/818667/
    """

    def __init__(self, session: AsyncSession | AsyncTransaction):
        self.session = session

    async def make_request(self, query: str, **kwargs) -> AsyncResult:
        try:
            result: AsyncResult = await self.session.run(query=query, **kwargs)
        except asyncio.CancelledError:
            self.session.cancel()
            raise
        else:
            return result
