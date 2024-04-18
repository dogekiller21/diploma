from typing import Union

from fastapi import FastAPI, Depends

from app.routers import crud_router
from db.session import get_db_session

app = FastAPI()

app.include_router(crud_router)
