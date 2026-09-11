"""added oauth accounts

Revision ID: a44c4a3197c1
Revises: 0e8f46882d20
Create Date: 2026-09-11 19:39:49.714836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a44c4a3197c1'
down_revision: Union[str, Sequence[str], None] = '0e8f46882d20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('oauth_accounts',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('provider_user_id', sa.String(length=255), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_accounts_provider_subject')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('oauth_accounts')
