### Core modules ###
from pydantic import BaseModel
from uuid import UUID


### Type hints ###


### Internal modules ###
from ...apis.data_models.emissions import (
    EmissionsPublic,
    EmissionsDelete
)



"""
Client responses format according to FE requirements.
"""
class EmissionsPublicResponse(BaseModel):
    success:    bool
    count:      int
    result:     list[EmissionsPublic]


class EmissionsCreateResponse(BaseModel):
    success:    bool
    created:    EmissionsPublic


class EmissionsDeleteResponse(BaseModel):
    success:    bool
    deleted:    EmissionsDelete

class EmissionsMonthlyStatsResponse(BaseModel):
    success: bool
    year: int
    monthly_totals: list[float | None]  # exactly 12 values, index 0 = Jan


class EmissionsUserSummaryResponse(BaseModel):
    success: bool
    user_id: UUID
    total_emissions: float
    total_cpu_power: float
    total_gpu_power: float


class EmissionsUserRollingResponse(BaseModel):
    success: bool
    user_id: UUID
    months: int
    labels: list[str]
    totals: list[float | None]

