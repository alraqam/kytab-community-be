"""added_feature_flags

Revision ID: f44e1d6dab2b
Revises: a44c4a3197c1
Create Date: 2026-09-12 16:20:44.705531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f44e1d6dab2b'
down_revision: Union[str, Sequence[str], None] = 'a44c4a3197c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('feature_flags',
    sa.Column('created_by_id', sa.BigInteger(), nullable=False),
    sa.Column('key', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.Column('rollout_percentage', sa.Integer(), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key', name='uq_feature_flags_key')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('feature_flags')
