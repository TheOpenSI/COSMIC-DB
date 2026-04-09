### Core modules ###
from sqlmodel import SQLModel


### Type hints ###


### Internal modules ###
from ...apis.data_models.services import (
    ServicePublic,
    ServiceDelete
)



"""
Client responses format according to FE requirements.
"""
class ServicesPublicResponse(SQLModel):
    success:    bool
    count:      int
    result:     list[ServicePublic]


class ServiceCreateResponse(SQLModel):
    success:    bool
    created:    ServicePublic


class ServicePublicResponse(SQLModel):
    success:    bool
    result:     ServicePublic


class ServiceUpdateResponse(SQLModel):
    success:    bool
    updated:    ServicePublic


class ServiceDeleteResponse(SQLModel):
    success:    bool
    deleted:    ServiceDelete
