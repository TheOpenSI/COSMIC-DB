### Core modules ###
from pydantic import BaseModel


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
    success:    bool
    count:      int
    result:     list[ConfigurationPublic]


class ConfigurationCreateResponse(BaseModel):
    success:    bool
    created:    ConfigurationPublic


class ConfigurationPublicResponse(BaseModel):
    success:    bool
    result:     ConfigurationPublic

class ConfigurationUpdateResponse(BaseModel):
    success:    bool
    updated:    ConfigurationPublic


class ConfigurationDeleteResponse(BaseModel):
    success:    bool
    deleted:    ConfigurationDelete
