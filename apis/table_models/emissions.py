### Core modules ###
from sqlmodel import (
    Field,
)
from sqlalchemy.schema import (
    PrimaryKeyConstraint,
)


### Type hints ###
from datetime import datetime, timezone
from uuid import UUID, uuid7
from sqlalchemy.sql.sqltypes import (
    TIMESTAMP,
    Uuid
)
from typing import (
    Optional
)


### Internal modules ###
from ..base_models import EmissionsBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class Emissions(EmissionsBase, table=True):
    __tablename__: str = "emissions" # pyright: ignore
    __table_args__: tuple[
        PrimaryKeyConstraint,
    ] = (
        PrimaryKeyConstraint(
            "id",
            name="PK_EMISSIONS_ID"
        ),
    )

    id: UUID = Field(
        default_factory=(lambda: uuid7()),
        nullable=False,
        sa_type=Uuid(
            as_uuid=True,
            native_uuid=True
        ) # pyright: ignore
    )
    timestamp: datetime = Field(
        default_factory=(lambda: datetime.now(tz=timezone.utc)),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True) # pyright: ignore
    )
