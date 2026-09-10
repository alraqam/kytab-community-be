"""added_club_member_cap

Revision ID: ba3d78ac806d
Revises: 9a1f5c3e7b2d
Create Date: 2026-09-10 23:32:52.643704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba3d78ac806d'
down_revision: Union[str, Sequence[str], None] = '9a1f5c3e7b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('clubs', sa.Column('member_cap', sa.Integer(), nullable=False, server_default='150'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('clubs', 'member_cap')
