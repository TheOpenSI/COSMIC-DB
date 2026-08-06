""" user_identities table

Revision ID: 150dab052233
Revises: b811fd75d9b8
Create Date: 2026-07-29 13:18:02.387585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '150dab052233'
down_revision: Union[str, Sequence[str], None] = 'b811fd75d9b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_identities",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.VARCHAR(length=50), nullable=False),
        sa.Column("sub", sa.VARCHAR(length=255), nullable=False),
        sa.Column("created_on", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("PK_USER_IDENTITY_ID")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("FK_USER_IDENTITY_USER_ID"),
            onupdate="CASCADE",
            ondelete="CASCADE",
            match="FULL",
        ),
        sa.UniqueConstraint(
            "provider",
            "sub",
            name=op.f("UK_USER_IDENTITY_PROVIDER_SUB"),
        ),
    )


def downgrade() -> None:
    op.drop_table("user_identities")
