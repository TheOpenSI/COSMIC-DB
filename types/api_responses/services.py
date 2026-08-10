### Core modules ###
from pydantic import (
    BaseModel,
    ConfigDict
)


### Type hints ###


### Internal modules ###
from ...apis.data_models.services import (
    ServicePublic,
    ServiceDelete
)



"""
Client responses format according to FE requirements.
"""
class ServicesPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    count:      int
    result:     list[ServicePublic]


class ServiceCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    created:    ServicePublic


class ServicePublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    result:     ServicePublic


class ServiceUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    updated:    ServicePublic


class ServiceDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    deleted:    ServiceDelete
