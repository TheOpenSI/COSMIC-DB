### Core modules ###
from pydantic import ConfigDict


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
    id:         UUID
    create_on:  datetime


class RoleCreate(RoleBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    pass


class RoleUpdate(RoleBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    name:       str | None = None # pyright: ignore
    desc:       str | None = None


class RoleDelete(RoleBase):
    id:         UUID
    create_on:  datetime
