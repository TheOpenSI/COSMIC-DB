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
    model_config = ConfigDict(extra="forbid")           # pyright: ignore

    pass


class EmissionsUpdate(EmissionsBase):
    model_config = ConfigDict(extra="forbid")           # pyright: ignore

    run_id: UUID7 | None                          = None  # pyright: ignore
    duration: float | None                      = None  # pyright: ignore
    emissions: float | None                     = None  # pyright: ignore
    emissions_rate: float | None                = None  # pyright: ignore
    cpu_power: float | None                     = None  # pyright: ignore
    gpu_power: float | None                     = None  # pyright: ignore
    ram_power: float | None                     = None  # pyright: ignore
    cpu_energy: float | None                    = None  # pyright: ignore
    gpu_energy: float | None                    = None  # pyright: ignore
    ram_energy: float | None                    = None  # pyright: ignore
    energy_consumed: float | None               = None  # pyright: ignore
    water_consumed: float | None                = None  # pyright: ignore


class EmissionsDelete(EmissionsBase):
    id:         UUID7
    timestamp:  AwareDatetime


class EmissionsDelete(EmissionsBase):
    id:         UUID7
    timestamp:  AwareDatetime
