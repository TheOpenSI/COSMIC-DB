### Core modules ###
from sqlmodel import SQLModel


### Type hints ###
from pydantic.types import AwareDatetime


### Internal modules ###



#=============================================================================#
#           Pydantic validation for chat history format (JSONB type)          #
#=============================================================================#
class ChatboxResponse(SQLModel):
    """docstring for ChatboxResponse."""
    # NOTE:
    # If edit/share convo pairs feature added, then we can use 'convo_pair_id'
    # UUID value.
    user:               str
    query_create_on:    AwareDatetime
    assitant:           str
    response_create_on: AwareDatetime
