"""added_discussion_prompts

Revision ID: 95dbcbd21a5b
Revises: b0fa09486033
Create Date: 2026-08-02 17:24:28.937437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95dbcbd21a5b'
down_revision: Union[str, Sequence[str], None] = 'b0fa09486033'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('discussion_prompts',
    sa.Column('milestone_id', sa.BigInteger(), nullable=False),
    sa.Column('created_by_id', sa.BigInteger(), nullable=False),
    sa.Column('text', sa.String(length=512), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('discussion_prompts')
