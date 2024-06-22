import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1 import router as api_router
from app.config.app import ADMIN_PASSWORD, SECRET_KEY
from app.db.neo4j.session import execute_with_session
from app.db.postgresql.models.base import Base
from app.db.postgresql.models.dbuser import DBUser
from app.db.postgresql.session import AsyncSessionLocal, async_engine
from app.exceptions.frontend import FrontendNotAuthException
from app.exceptions.handlers import frontend_not_auth_exception_handler
from app.frontend.misc import templates
from app.frontend.routers import front_router

logger = logging.getLogger(__name__)


app = FastAPI(
    title="FirmwaresHub", docs_url="/api/docs", redoc_url="/api/redoc", version="0.1.1"
)


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing constraints...")
    try:
        query = """
        CREATE CONSTRAINT unique_numberplate IF NOT EXISTS
        FOR (c:Car)
        REQUIRE c.numberplate IS UNIQUE;
        """
        await execute_with_session(query=query)
    except Exception as e:
        logger.error("Error initializing constraints: %s", e, exc_info=e)

    logger.info("Creating postgresql db tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        logger.info("Ensuring postgres admin user exists...")
        await DBUser.create_admin_if_not_exists(
            session=session, password=ADMIN_PASSWORD
        )

    logger.info("Initialization complete")


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(api_router)
app.include_router(front_router)
# noinspection PyTypeChecker
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# noinspection PyTypeChecker
app.add_exception_handler(FrontendNotAuthException, frontend_not_auth_exception_handler)
