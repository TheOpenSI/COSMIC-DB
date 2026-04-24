### Core modules ###
from pydantic import BaseModel


### Type hints ###


### Internal modules ###
from ...apis.data_models.chatboxes import (
    ChatboxPublic,
    ChatboxPublicWithUser
)



"""
Client responses format according to FE requirements.
"""
class ChatboxesPublicResponse(BaseModel):
    success:    bool
    count:      int
    result:     list[ChatboxPublicWithUser]


class ChatboxCreateResponse(BaseModel):
    success:    bool
    created:    ChatboxPublic


class ChatboxPublicResponse(BaseModel):
    success:    bool
    result:     ChatboxPublicWithUser
