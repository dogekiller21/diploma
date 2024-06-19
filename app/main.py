from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as api_router
from app.routers import front_router

app = FastAPI(
    title="FirmwaresHub", docs_url="/api/docs", redoc_url="/api/redoc", version="0.1.1"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)
app.include_router(front_router)
