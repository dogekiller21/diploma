from neo4j import AsyncGraphDatabase

from app.config.db import DB_NAME, DB_PASSWORD, DB_USERNAME
from app.db.misc import get_db_uri

driver = AsyncGraphDatabase.driver(uri=get_db_uri(), auth=(DB_USERNAME, DB_PASSWORD))


async def get_db_session():
    session = driver.session(database=DB_NAME)
    try:
        yield session
    finally:
        await session.close()
