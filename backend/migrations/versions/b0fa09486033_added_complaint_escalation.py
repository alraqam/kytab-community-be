"""added_complaint_escalation

Revision ID: b0fa09486033
Revises: 2ea5e246dd6c
Create Date: 2026-08-02 17:24:28.543723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0fa09486033'
down_revision: Union[str, Sequence[str], None] = '2ea5e246dd6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('complaint', sa.Column('is_escalated', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('complaint', 'is_escalated')
