"""drop chat_id from emissions

Revision ID: bb438641b88c
Revises: 4ad2ba43cfbf
Create Date: 2026-06-08 09:44:28.931362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb438641b88c'
down_revision: Union[str, Sequence[str], None] = '4ad2ba43cfbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("emissions", "chat_id")


def downgrade() -> None:
    op.add_column(
        "emissions",
        sa.Column(
            "chat_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
