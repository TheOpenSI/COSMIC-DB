### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)


### Internal modules ###
from ..base_models import RoleBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class RolePublic(RoleBase):
    name:       str
    id:         UUID7
    create_on:  AwareDatetime


class RoleCreate(RoleBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    pass


class RoleUpdate(RoleBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    name:       str | None = None # pyright: ignore
    desc:       str | None = None


class RoleDelete(RoleBase):
    name:       str
    id:         UUID
    create_on:  datetime
