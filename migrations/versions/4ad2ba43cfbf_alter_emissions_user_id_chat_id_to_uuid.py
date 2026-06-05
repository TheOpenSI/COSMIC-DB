"""alter emissions user_id chat_id to uuid

Revision ID: 4ad2ba43cfbf
Revises: b811fd75d9b8
Create Date: 2026-06-05 01:03:01.376836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ad2ba43cfbf'
down_revision: Union[str, Sequence[str], None] = 'b811fd75d9b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name="emissions",
        column_name="user_id",
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        postgresql_using="user_id::uuid",  
        nullable=True
    )
    op.alter_column(
        table_name="emissions",
        column_name="chat_id",
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        postgresql_using="chat_id::uuid",   
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        table_name="emissions",
        column_name="user_id",
        type_=sa.VARCHAR(length=255),
        nullable=True
    )
    op.alter_column(
        table_name="emissions",
        column_name="chat_id",
        type_=sa.VARCHAR(length=255),
        nullable=True
    )
