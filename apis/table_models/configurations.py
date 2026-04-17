### Core modules ###
from sqlmodel import Field
from sqlalchemy.schema import PrimaryKeyConstraint


### Type hints ###
from datetime import (
    datetime,
    timezone
)
from uuid import (
    UUID,
    uuid7
)
from sqlalchemy.sql.sqltypes import (
    TIMESTAMP,
    Uuid
)


### Internal modules ###
from ..base_models import ConfigurationBase



"""
To understand how this file structured, take a look at:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class Configurations(ConfigurationBase, table=True):
    __tablename__: str = "configurations" # pyright: ignore
    __table_args__: tuple[
        PrimaryKeyConstraint,
    ] = (
        PrimaryKeyConstraint(
            "id",
            name="PK_CONFIGURATION_ID"
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
    create_on: datetime = Field(
        default_factory=(lambda: datetime.now(tz=timezone.utc)),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True) # pyright: ignore
    )
