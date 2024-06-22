from enum import Enum
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel

from app.models import as_form


class UserScopeEnum(str, Enum):
    user = "user"
    admin = "admin"


class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    scope: UserScopeEnum

    class Config:
        from_attributes = True
