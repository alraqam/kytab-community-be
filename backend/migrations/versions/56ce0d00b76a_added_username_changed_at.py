"""added_username_changed_at

Revision ID: 56ce0d00b76a
Revises: 95dbcbd21a5b
Create Date: 2026-08-23 16:45:26.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56ce0d00b76a'
down_revision: Union[str, Sequence[str], None] = '95dbcbd21a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('username_changed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'username_changed_at')
