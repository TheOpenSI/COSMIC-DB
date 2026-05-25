### Core modules ###
from sqlmodel import SQLModel


### Type hints ###


### Internal modules ###
from ...apis.data_models.roles import (
    RolePublic,
    RoleDelete
)



"""
Client responses format according to FE requirements.
"""
class RolesPublicResponse(SQLModel):
    success:    bool
    count:      int
    result:     list[RolePublic]


class RoleCreateResponse(SQLModel):
    success:    bool
    created:    RolePublic


class RolePublicResponse(SQLModel):
    success:    bool
    result:     RolePublic


class RoleUpdateResponse(SQLModel):
    success:    bool
    updated:    RolePublic


class RoleDeleteResponse(SQLModel):
    success:    bool
    deleted:    RoleDelete
