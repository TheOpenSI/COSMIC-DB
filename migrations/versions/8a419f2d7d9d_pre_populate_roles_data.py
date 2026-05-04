"""pre_populate_roles_data

Revision ID: 8a419f2d7d9d
Revises: 
Create Date: 2026-05-04 11:17:34.760078

"""
from datetime import datetime, timezone
from typing import Sequence, Union
from uuid import UUID, uuid7

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a419f2d7d9d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Define pre-population tables
    roles_table: sa.Table = op.create_table(
        'roles',
        sa.Column('id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('desc', sa.TEXT(length=None, collation=None), autoincrement=False, nullable=True),
        sa.Column('create_on', sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_ROLE_ID')),
        sa.UniqueConstraint('name', name=op.f(name='UK_ROLE_NAME'), postgresql_include=[], postgresql_nulls_not_distinct=False),
        if_not_exists=True
    )

    # Define data to pre-populate to 'Users' table
    roles_data: list[dict[str, UUID | str | datetime]] = [
        {
            'id': uuid7(),
            'name': 'Admin',
            'desc': 'Has full administrative rights to configure CoSMIC, including selecting and managing models, adjusting RAG thresholds, and enabling or disabling available services.',
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            'id': uuid7(),
            'name': 'User',
            'desc': 'Can use CoSMIC but cannot change its configuration',
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            # NOTE:
            # Only LLM response need this role. Can be validate from FE/BE
            # depends on the business logic
            'id': uuid7(),
            'name': 'Assistant',
            'desc': 'Allow chat history to differenciate question from user and response from LLM. Only used for LLM responses.',
            'create_on': datetime.now(tz=timezone.utc)
        }
    ]

    # Pre-populating in bulk (insertion order matters)
    op.bulk_insert(
        table=roles_table,
        rows=roles_data,
        multiinsert=True # Set to 'False' if pass in pre-populate data literally
    )

    return None


def downgrade() -> None:
    """Downgrade schema."""
    # Wipes table, any FK relationship, and its data automatically since this's
    # just a fresh run
    op.drop_table(
        table_name='roles',
        schema='public',
        if_exists=True
    )

    return None
