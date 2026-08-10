### Core modules ###
from pydantic import (
    BaseModel,
    ConfigDict
)


### Type hints ###


### Internal modules ###
from ...apis.data_models.configurations import (
    ConfigurationPublic,
    ConfigurationDelete
)



"""
Client responses format according to FE requirements.
"""
class ConfigurationsPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    count:      int
    result:     list[ConfigurationPublic]


class ConfigurationCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    created:    ConfigurationPublic


class ConfigurationPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    result:     ConfigurationPublic

class ConfigurationUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    updated:    ConfigurationPublic


class ConfigurationDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    deleted:    ConfigurationDelete
