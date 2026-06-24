### Core modules ###
from pydantic import BaseModel


### Type hints ###


### Internal modules ###
from ...apis.data_models.emissions import (
    EmissionPublic,
    EmissionDelete
)



"""
Client responses format according to FE requirements.
"""
class EmissionsPublicResponse(BaseModel):
    success:    bool
    count:      int
    result:     list[EmissionPublic]


class EmissionCreateResponse(BaseModel):
    success:    bool
    created:    EmissionPublic


class EmissionDeleteResponse(BaseModel):
    success:    bool
    deleted:    EmissionDelete
