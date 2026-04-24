### Core modules ###
from pydantic import ConfigDict


### Type hints ###
from datetime import datetime
from uuid import UUID


### Internal modules ###
from ..base_models import ChatboxBase
from ..data_models.users import UserPublicWithRole



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class ChatboxPublic(ChatboxBase):
    id:         UUID
    create_on:  datetime


class ChatboxPublicWithUser(ChatboxPublic):
    user:       UserPublicWithRole | None = None


class ChatboxCreate(ChatboxBase):
    model_config = ConfigDict(extra="forbid") # pyright: ignore

    pass
