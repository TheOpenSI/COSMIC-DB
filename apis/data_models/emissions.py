### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)


### Internal modules ###
from ..base_models import EmissionBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class EmissionPublic(EmissionBase):
    id:         UUID7
    timestamp:  AwareDatetime


class EmissionCreate(EmissionBase):
    model_config = ConfigDict(extra="forbid") # pyright: ignore

    pass


class EmissionDelete(EmissionBase):
    id:         UUID7
    timestamp:  AwareDatetime
