### Core modules ###
from pydantic import BaseModel, ConfigDict


### Type hints ###
from pydantic.types import AwareDatetime


### Internal modules ###



#=============================================================================#
#           Pydantic validation for chat history format (JSONB type)          #
#=============================================================================#
class ChatHistorySchema(BaseModel):
    """docstring for ChatHistorySchema."""
    model_config = ConfigDict(extra="forbid")

    # NOTE:
    # If edit/share convo pairs feature added, then we can use 'convo_pair_id'
    # UUID value.
    user_role:          str
    user_query:         str
    query_create_on:    AwareDatetime
    llm_role:           str
    llm_response:       str
    response_create_on: AwareDatetime
