### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from datetime import datetime
from pydantic.types import PositiveInt


### Internal modules ###
from ..base_models import ServiceBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class ServicePublic(ServiceBase):
    id:         PositiveInt
    create_on:  datetime


class ServiceCreate(ServiceBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    pass


class ServiceUpdate(ServiceBase):
    model_config = ConfigDict(extra="forbid")   # pyright: ignore

    name:           str | None  = None          # pyright: ignore
    desc:           str | None  = None
    status:         bool | None = True          # pyright: ignore
    rag_capability: bool | None = False         # pyright: ignore


class ServiceDelete(ServiceBase):
    id:         PositiveInt
    create_on:  datetime
