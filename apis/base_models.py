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
from sqlalchemy.dialects.postgresql import JSONB
from ..types.api_responses.configurations import ConfigurationSchema


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


class ConfigurationBase(SQLModel):
    name: str | None = Field(
        default=None,
        nullable=True,
        sa_type=Text(
            length=None,
            collation=None
        ) # pyright: ignore
    )
    details: ConfigurationSchema = Field(
        nullable=False,
        sa_type=JSONB(
            none_as_null=True,
            astext_type=None
        ) # pyright: ignore
    )
