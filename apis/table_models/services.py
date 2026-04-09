### Core modules ###
from sqlmodel import Field


### Type hints ###
from datetime import (
    datetime,
    timezone
)
from sqlalchemy.sql.schema import (
    PrimaryKeyConstraint
)
from sqlalchemy.sql.sqltypes import (
    TIMESTAMP,
    Boolean,
    SmallInteger
)


### Internal modules ###
from ..base_models import ServiceBase



"""
For reference on how this directory structured:
https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
"""
class Services(ServiceBase, table=True):
    __tablename__: str = "services" # pyright: ignore
    __table_args__: tuple[
        PrimaryKeyConstraint,
    ] = (
        PrimaryKeyConstraint(
            "id",
            name="PK_SERVICE_ID"
        ),
    )

    status: bool = Field(
        default=False,
        nullable=False,
        sa_type=Boolean(
            create_constraint=False,
            name=None
        ) # pyright: ignore
    )

    """
    SQLModel (SQLAlchemy under the hood) doesn't have a clear way to create a
    table with PostgreSQL's SERIAL column data type. No problems, it's just
    SMALLINT + AUTO_INCREMENT after all. However, there aren't any single clear
    example given from both wrapper and its child library. Okay... I'm surely
    can find a way to do this without having to manually write SQL statement
    here, we're using ORM!! Welp, I did manage to get it working, but for other
    to understand how, please take a look on these 4 reference links I provided
    below:

    1. https://github.com/fastapi/sqlmodel/blob/main/sqlmodel/main.py (Line 740)
    2. https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#sequences-serial-identity
    3. https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-SERIAL
    4. https://stackoverflow.com/questions/21328599/why-isnt-sqlalchemy-creating-serial-columns/21346262#21346262
    """

    id: int | None = Field(
        default=None,
        nullable=False,
        sa_type=SmallInteger(), # pyright: ignore
    )
    create_on: datetime = Field(
        default_factory=(lambda: datetime.now(tz=timezone.utc)),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True) # pyright: ignore
    )
