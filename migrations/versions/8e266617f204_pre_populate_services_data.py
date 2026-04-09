"""pre_populate_services_data

Revision ID: 8e266617f204
Revises: 96121362751e
Create Date: 2026-04-09 19:18:21.770339

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = '8e266617f204'
down_revision: Union[str, Sequence[str], None] = '96121362751e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

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

    # Define pre-population tables
    services_table: sa.Table = op.create_table(
        'services',
        sa.Column('id', sa.SMALLINT(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=100, collation=None), autoincrement=False, nullable=False),
        sa.Column('desc', sa.TEXT(length=None, collation=None), autoincrement=False, nullable=True),
        sa.Column('status', sa.BOOLEAN(create_constraint=False, name=None), autoincrement=False, nullable=False, default=False),
        sa.Column('create_on', sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_SERVICE_ID')),
        if_not_exists=True
    )

    # Define data to pre-populate to 'Services' table
    services_data: list[dict[str, int | str | datetime]] = [
        {
            # No need to specify 'id' column here as PostgreSQL will perform an
            # auto increment for us with SMALLSERIAL data type (which is
            # SMALLINT + AUTO INCREMENT under the hood)
            'name': 'chess',
            'desc': 'If it is a chess game, predict the next chess move by providing a sequence of moves or a FEN.',
            'status': True,
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            # No need to specify 'id' column here as PostgreSQL will perform an
            # auto increment for us with SMALLSERIAL data type (which is
            # SMALLINT + AUTO INCREMENT under the hood)
            'name': 'memory',
            'desc': 'Update the vector database with a declarative sentence (not a question), or a PDF document.',
            'status': True,
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            # No need to specify 'id' column here as PostgreSQL will perform an
            # auto increment for us with SMALLSERIAL data type (which is
            # SMALLINT + AUTO INCREMENT under the hood)
            'name': 'code_generation',
            'desc': 'Generate or improve a code or answer a question in order to generate or improve a code.',
            'status': True,
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            # No need to specify 'id' column here as PostgreSQL will perform an
            # auto increment for us with SMALLSERIAL data type (which is
            # SMALLINT + AUTO INCREMENT under the hood)
            'name': 'general_question_answering',
            'desc': 'Answer a question or provide a reasoning, which cannot be achieved by the other services.',
            'status': True,
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            # No need to specify 'id' column here as PostgreSQL will perform an
            # auto increment for us with SMALLSERIAL data type (which is
            # SMALLINT + AUTO INCREMENT under the hood)
            'name': 'academic_governance',
            'desc': 'Answer question about Academic Governance.',
            'status': True,
            'create_on': datetime.now(tz=timezone.utc)
        }
    ]

    # Pre-populating in bulk (insertion order matters)
    op.bulk_insert(
        table=services_table,
        rows=services_data,
        multiinsert=True # Set to 'False' if pass in pre-populate data literally
    )

    return None


def downgrade() -> None:
    """Downgrade schema."""
    # Wipes table, any FK relationship, and its data automatically since this's
    # just a fresh run
    op.drop_table(
        table_name='services',
        schema='public',
        if_exists=True
    )

    return None
