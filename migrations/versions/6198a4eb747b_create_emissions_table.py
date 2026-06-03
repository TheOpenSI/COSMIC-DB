"""create emissions table

Revision ID: 6198a4eb747b
Revises: a3e40b0c0b7b
Create Date: 2026-06-03 15:23:12.270652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6198a4eb747b'
down_revision: Union[str, Sequence[str], None] = 'a3e40b0c0b7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Define table schemas
    op.create_table(
        'emissions',
        sa.Column('id', sa.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('project_name', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('run_id', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('experiment_id', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=False),
        sa.Column('duration', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('emissions', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('emissions_rate', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('cpu_power', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('gpu_power', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('ram_power', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('cpu_energy', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('gpu_energy', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('ram_energy', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('energy_consumed', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('water_consumed', sa.Float(), autoincrement=False, nullable=False),
        sa.Column('country_name', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('country_iso_code', sa.VARCHAR(length=10, collation=None), autoincrement=False, nullable=True),
        sa.Column('region', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('cloud_provider', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('cloud_region', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('os', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('python_version', sa.VARCHAR(length=50, collation=None), autoincrement=False, nullable=True),
        sa.Column('codecarbon_version', sa.VARCHAR(length=50, collation=None), autoincrement=False, nullable=True),
        sa.Column('cpu_count', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('cpu_model', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('gpu_count', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('gpu_model', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('longitude', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('latitude', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('ram_total_size', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('tracking_mode', sa.VARCHAR(length=50, collation=None), autoincrement=False, nullable=True),
        sa.Column('cpu_utilization_percent', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('gpu_utilization_percent', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('ram_utilization_percent', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('ram_used_gb', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('on_cloud', sa.VARCHAR(length=1, collation=None), autoincrement=False, nullable=True),
        sa.Column('pue', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('wue', sa.Float(), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.Column('chat_id', sa.VARCHAR(length=255, collation=None), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f(name='PK_EMISSIONS_ID')),
        if_not_exists=True
    )

    return None


def downgrade() -> None:
    """Downgrade schema."""
    # Wipes table, any FK relationship, and its data automatically since this's
    # just a fresh run
    op.drop_table(
        table_name='emissions',
        schema='public',
        if_exists=True
    )

    return None
