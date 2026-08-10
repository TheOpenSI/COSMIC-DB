### Core modules ###
from pydantic import (
    BaseModel,
    ConfigDict
)


### Type hints ###


### Internal modules ###
from ...apis.data_models.chatboxes import (
    ChatboxPublic,
    ChatboxDelete
)



"""
Client responses format according to FE requirements.
"""
class ChatboxesPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    count:      int
    result:     list[ChatboxPublic]


class ChatboxCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    created:    ChatboxPublic


class ChatboxPublicResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    result:     ChatboxPublic


class ChatboxUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    updated:    ChatboxPublic


class ChatboxDeleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success:    bool
    deleted:    ChatboxDelete
