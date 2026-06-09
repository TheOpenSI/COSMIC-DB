### Core modules ###
from pydantic import BaseModel


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
