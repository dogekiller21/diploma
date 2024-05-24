from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import crud_router, front_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(crud_router)
app.include_router(front_router)
