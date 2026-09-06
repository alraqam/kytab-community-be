"""added_push_subscriptions_and_digest_tracking

Revision ID: a7f266bc7641
Revises: 56ce0d00b76a
Create Date: 2026-09-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7f266bc7641'
down_revision: Union[str, Sequence[str], None] = '56ce0d00b76a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notification_preferences', sa.Column('last_digest_sent_at', sa.DateTime(), nullable=True))
    op.create_table('push_subscriptions',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('endpoint', sa.Text(), nullable=False),
    sa.Column('p256dh', sa.String(length=255), nullable=False),
    sa.Column('auth', sa.String(length=255), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('endpoint')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('push_subscriptions')
    op.drop_column('notification_preferences', 'last_digest_sent_at')
