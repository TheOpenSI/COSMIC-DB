### Core modules ###


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
    status:     bool = False
    id:         PositiveInt
    create_on:  datetime


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(ServiceBase):
    name:       str | None = None   # pyright: ignore
    desc:       str | None = None
    status:     bool | None = True  # pyright: ignore


class ServiceDelete(ServiceBase):
     # WARNING: === ONLY DELETE DEACTIVATED SERVICES ===
    status:     bool = False
    id:         PositiveInt
    create_on:  datetime
