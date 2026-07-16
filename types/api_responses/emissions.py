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
    success: bool
    year: int
    monthly_totals: list[float | None]  # exactly 12 values, index 0 = Jan


class EmissionsUserSummaryResponse(BaseModel):
    success: bool
    user_id: UUID7
    total_emissions: float
    total_cpu_power: float
    total_gpu_power: float


class EmissionsUserRollingResponse(BaseModel):
    success: bool
    user_id: UUID7
    months: int
    labels: list[str]
    totals: list[float | None]
