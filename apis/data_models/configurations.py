### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)


### Internal modules ###
from ..base_models import ConfigurationBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class ConfigurationPublic(ConfigurationBase):
    id:         UUID7
    create_on:  AwareDatetime


class ConfigurationCreate(ConfigurationBase):
    model_config = ConfigDict(extra="forbid") # pyright: ignore

    pass
