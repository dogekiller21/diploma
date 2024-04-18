from fastapi import FastAPI

from app.routers import crud_router

app = FastAPI()

app.include_router(crud_router)
