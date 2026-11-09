"""added_club_opening_reason

Revision ID: 3b7e1d9c4a52
Revises: 97aca8d3ae6d
Create Date: 2026-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b7e1d9c4a52'
down_revision: Union[str, Sequence[str], None] = '97aca8d3ae6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('clubs', sa.Column('opening_reason', sa.String(length=1024), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('clubs', 'opening_reason')
