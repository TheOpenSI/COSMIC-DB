### Core modules ###
from pydantic import (
    BaseModel,
    ConfigDict
)


### Type hints ###


### Internal modules ###
from ...apis.data_models.roles import (
    RolePublic,
    RoleDelete
)



"""
Client responses format according to FE requirements.
"""
class RolesPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    count:      int
    result:     list[RolePublic]


class RoleCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    created:    RolePublic


class RolePublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    result:     RolePublic


class RoleUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    updated:    RolePublic


class RoleDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    deleted:    RoleDelete
