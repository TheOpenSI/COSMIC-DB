### Core modules ###
from sqlmodel import (
    Field,
    SQLModel
)


### Type hints ###
from uuid import UUID
from sqlalchemy.sql.sqltypes import (
    VARCHAR,
    Text,
    Uuid
)
from typing import Any
from sqlalchemy.dialects.postgresql import JSONB


### Internal modules ###



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class UserBase(SQLModel):
    role_id: UUID = Field(
        nullable=False,
        sa_type=Uuid(
            as_uuid=True,
            native_uuid=True
        ) # pyright: ignore
    )
    name: str = Field(
        max_length=255,
        nullable=False,
        sa_type=VARCHAR(
            length=255,
            collation=None
        ) # pyright: ignore
    )


class RoleBase(SQLModel):
    desc: str | None = Field(
        default=None,
        nullable=True,
        sa_type=Text(
            length=None,
            collation=None
        ) # pyright: ignore
    )


class ServiceBase(SQLModel):
    name: str = Field(
        max_length=100,
        nullable=False,
        sa_type=VARCHAR(
            length=100,
            collation=None
        ) # pyright: ignore
    )
    desc: str | None = Field(
        default=None,
        nullable=True,
        sa_type=Text(
            length=None,
            collation=None
        ) # pyright: ignore
    )


class ChatboxBase(SQLModel):
    user_id: UUID = Field(
        nullable=False,
        sa_type=Uuid(
            as_uuid=True,
            native_uuid=True
        ) # pyright: ignore
    )
    name: str = Field(
        max_length=256,
        nullable=False,
        sa_type=Text(
            length=None,
            collation=None
        ) # pyright: ignore
    )
    details: dict[str, Any] = Field(
        # TODO:
        # Chat history format. We need to have a chat with the team first as this
        # can get very complicated to modify later on if we just trying to add
        # features one by one without having a fairly acceptable database design
        # on this.
        # default={},
        nullable=False,
        sa_type=JSONB(
            none_as_null=True,
            astext_type=None
        ) # pyright: ignore
    )
