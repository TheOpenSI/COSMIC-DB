### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from pydantic.types import (
    UUID7,
    AwareDatetime
)
from ...types.json_schemas import ChatHistorySchema


### Internal modules ###
from ..base_models import ChatboxBase
from ..data_models.users import UserPublicWithRole



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class ChatboxPublic(ChatboxBase):
    id:         UUID7
    create_on:  AwareDatetime


class ChatboxPublicWithUser(ChatboxPublic):
    user:       UserPublicWithRole | None = None


class ChatboxCreate(ChatboxBase):
    model_config = ConfigDict(extra="forbid")           # pyright: ignore

    pass


class ChatboxUpdate(ChatboxBase):
    model_config = ConfigDict(extra="forbid")           # pyright: ignore

    user_id:    UUID7 | None                    = None  # pyright: ignore
    name:       str | None                      = None  # pyright: ignore
    details:    list[ChatHistorySchema] | None  = None  # pyright: ignore


class ChatboxDelete(ChatboxBase):
    id:         UUID7
    create_on:  AwareDatetime
