"""added_two_factor_auth

Revision ID: 0e8f46882d20
Revises: ba3d78ac806d
Create Date: 2026-09-11 07:22:20.415293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e8f46882d20'
down_revision: Union[str, Sequence[str], None] = 'ba3d78ac806d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('totp_secret', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('is_2fa_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table('recovery_codes',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('code_hash', sa.Text(), nullable=False),
    sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code_hash')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('recovery_codes')
    op.drop_column('users', 'is_2fa_enabled')
    op.drop_column('users', 'totp_secret')
