### Core modules ###


### Type hints ###
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID


### Internal modules ###
from ..base_models import ChatboxBase
from ..data_models.users import UserPublicWithRole
if TYPE_CHECKING:
    """
    This's to resolve circular import issues, take a look at:
    https://sqlmodel.tiangolo.com/tutorial/code-structure/#circular-imports
    """
    from ...types.api_responses.chatboxes import ChatboxResponse



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
    pass


class ChatboxUpdate(ChatboxBase):
    user_id:    UUID | None = None              # pyright: ignore
    name:       str | None = None               # pyright: ignore
    details:    ChatboxResponse | None = None   # pyright: ignore


class ChatboxDelete(ChatboxBase):
    id:         UUID
    create_on:  datetime
