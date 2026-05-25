### Core modules ###


### Type hints ###
from datetime import datetime
from uuid import UUID


### Internal modules ###
from ..base_models import RoleBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class RolePublic(RoleBase):
    name:       str
    id:         UUID
    create_on:  datetime


class RoleCreate(RoleBase):
    name:       str


class RoleUpdate(RoleBase):
    name:       str | None = None # pyright: ignore
    desc:       str | None = None


class RoleDelete(RoleBase):
    name:       str
    id:         UUID
    create_on:  datetime
