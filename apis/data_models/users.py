### Core modules ###


### Type hints ###
from datetime import datetime
from uuid import UUID
from pydantic.networks import EmailStr


### Internal modules ###
from ..base_models import UserBase
from ..data_models.roles import RolePublic



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class UserPublic(UserBase):
    email:      EmailStr | None = None
    id:         UUID
    create_on:  datetime


class UserPublicWithRole(UserPublic):
    role:       RolePublic | None = None


class UserCreate(UserBase):
    email:      EmailStr | None = None


class UserUpdate(UserBase):
    role_id:    UUID | None = None  # pyright: ignore
    name:       str | None = None   # pyright: ignore
    email:      EmailStr | None = None


class UserDelete(UserBase):
    email:      EmailStr | None = None
    id:         UUID
    create_on:  datetime
