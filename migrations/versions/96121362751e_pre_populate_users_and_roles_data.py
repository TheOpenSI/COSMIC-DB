"""pre_populate_users_and_roles_data

Revision ID: 96121362751e
Revises: 
Create Date: 2026-04-07 18:40:42.124555

"""
from datetime import datetime, timezone
from typing import Sequence, Union
from uuid import UUID, uuid7
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '96121362751e'
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
        sa.Column('create_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_ROLE_ID')),
        sa.UniqueConstraint('name', name=op.f(name='UK_ROLE_NAME'), postgresql_include=[], postgresql_nulls_not_distinct=False),
        if_not_exists=True
    )
    users_table: sa.Table = op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('role_id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('create_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('FK_USER_ROLE_ID'), onupdate='CASCADE', ondelete='CASCADE', match='FULL'),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_USER_ID')),
        sa.UniqueConstraint('email', name=op.f(name='UK_USER_EMAIL'), postgresql_include=[], postgresql_nulls_not_distinct=False),
        if_not_exists=True
    )

    # Define data to pre-populate to 'Roles' table
    # We define role ID from outside so it can be refer to Users FK correctly
    admin_role_id:  UUID = uuid7()
    user_role_id:   UUID = uuid7()

    roles_data: list[dict[str, UUID | str | datetime]] = [
        {
            'id': admin_role_id,
            'name': 'Admin',
            'desc': 'Has full administrative rights to configure CoSMIC, including selecting and managing models, adjusting RAG thresholds, and enabling or disabling available services.',
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            'id': user_role_id,
            'name': 'User',
            'desc': 'Can use CoSMIC but cannot change its configuration',
            'create_on': datetime.now(tz=timezone.utc)
        },
    ]

    # Define data to pre-populate to 'Users' table
    users_data: list[dict[str, UUID | str | None | datetime]] = [
        {
            'id': uuid7(),
            'role_id': admin_role_id,
            'name': 'cosmic',
            'email': 'opensi@canberra.edu.au',
            'create_on': datetime.now(tz=timezone.utc)
        },
        {
            'id': uuid7(),
            'role_id': user_role_id,
            'name': 'test_user',
            'email': None,
            'create_on': datetime.now(tz=timezone.utc)
        },
    ]

    # Pre-populating in bulk (insertion order matters)
    op.bulk_insert(
        table=roles_table,
        rows=roles_data,
        multiinsert=True # Set to 'False' if pass in pre-populate data literally
    )
    op.bulk_insert(
        table=users_table,
        rows=users_data,
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
    op.drop_table(
        table_name='users',
        schema='public',
        if_exists=True
    )

    return None
