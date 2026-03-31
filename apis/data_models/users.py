### Core modules ###


### Type hints ###
from datetime import datetime
from uuid import UUID
from pydantic.networks import EmailStr


### Internal modules ###
from ..base_models import UserBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class UserPublic(UserBase):
    email: EmailStr | None = None
    id: UUID
    create_on: datetime


class UserCreate(UserBase):
    email: EmailStr | None = None


class UserUpdate(UserBase):
    name:       str | None = None # type: ignore
    email:      EmailStr | None = None


class UserDelete(UserBase):
    id: UUID
    create_on: datetime
    response: dict[str, int | str] = {
        "status": 200,
        "message": "OK"
    }
