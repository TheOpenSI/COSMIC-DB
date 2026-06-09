### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)


### Internal modules ###
from ..base_models import EmissionsBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class EmissionsPublic(EmissionsBase):
    id:         UUID7
    timestamp:  AwareDatetime


class EmissionsCreate(EmissionsBase):
    model_config = ConfigDict(extra="forbid") # pyright: ignore

    pass


class EmissionsDelete(EmissionsBase):
    id:         UUID7
    timestamp:  AwareDatetime
