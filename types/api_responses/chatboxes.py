### Core modules ###
from pydantic import BaseModel


### Type hints ###
from pydantic_extra_types.pendulum_dt import DateTime


### Internal modules ###
from ...apis.data_models.chatboxes import (
    ChatboxPublic,
    ChatboxPublicWithUser,
    ChatboxDelete
)



#=============================================================================#
#           Pydantic validation for chat history format (JSONB type)          #
#=============================================================================#
class ChatboxResponse(BaseModel):
    """docstring for ChatboxResponse."""
    # NOTE:
    # If edit/share convo pairs feature added, then we can use 'convo_pair_id'
    # UUID value.
    user:               str
    query_create_on:    DateTime
    assitant:           str
    response_create_on: DateTime



#=============================================================================#
#           Client responses format according to FE requirements              #
#=============================================================================#
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


class ChatboxUpdateResponse(BaseModel):
    success:    bool
    updated:    ChatboxPublic


class ChatboxDeleteResponse(BaseModel):
    success:    bool
    deleted:    ChatboxDelete
