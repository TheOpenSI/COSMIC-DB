### Core modules ###
from pydantic import (
    BaseModel,
    ConfigDict
)


### Type hints ###

from pydantic.types import UUID7

### Internal modules ###
from ...apis.data_models.emissions import (
    EmissionPublic,
    EmissionDelete
)



"""
Client responses format according to FE requirements.
"""
class EmissionsPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    count:      int
    result:     list[EmissionPublic]


class EmissionCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    created:    EmissionPublic


class EmissionDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    deleted:    EmissionDelete


class EmissionsMonthlyStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:        bool
    year:           int
    # exactly 12 values, index 0 = Jan
    monthly_totals: list[float | None]


class EmissionsUserSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:            bool
    user_id:            UUID7
    total_emissions:    float
    total_cpu_power:    float
    total_gpu_power:    float


class EmissionsUserRollingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:            bool
    user_id:            UUID7
    months:             int
    labels:             list[str]
    totals:             list[float | None]
