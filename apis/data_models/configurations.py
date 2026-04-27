### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)
from ...types.json_schemas import ConfigurationSchema


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
    model_config = ConfigDict(extra="forbid")       # pyright: ignore

    pass


class ConfigurationUpdate(ConfigurationBase):
    model_config = ConfigDict(extra="forbid")       # pyright: ignore

    name:       str | None                  = None  # pyright: ignore
    details:    ConfigurationSchema | None  = None  # pyright: ignore


class ConfigurationDelete(ConfigurationBase):
    id:         UUID7
    create_on:  AwareDatetime
