"""create_chatboxes_table

Revision ID: 51a0ff6b910d
Revises: 8e266617f204
Create Date: 2026-05-02 13:32:01.924435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '51a0ff6b910d'
down_revision: Union[str, Sequence[str], None] = '8e266617f204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Define table schemas
    op.create_table(
        'chatboxes',
        sa.Column('id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('details', JSONB(none_as_null=True,astext_type=None), autoincrement=False, nullable=False),
        sa.Column('create_on', sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_CHATBOX_ID')),
        sa.ForeignKeyConstraint(columns=['user_id'], refcolumns=['users.id'], name=op.f(name='FK_CHATBOX_USER_ID'), onupdate='CASCADE', ondelete='CASCADE', match='FULL'),
        if_not_exists=True
    )

    return None


def downgrade() -> None:
    """Downgrade schema."""
    # Wipes table, any FK relationship, and its data automatically since this's
    # just a fresh run
    op.drop_table(
        table_name='chatboxes',
        schema='public',
        if_exists=True
    )

    return None
