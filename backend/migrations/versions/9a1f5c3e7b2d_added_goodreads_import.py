"""added_goodreads_import

Revision ID: 9a1f5c3e7b2d
Revises: 0452575bee58
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a1f5c3e7b2d'
down_revision: Union[str, Sequence[str], None] = '0452575bee58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('goodreads_import_rows',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('author_name', sa.String(length=512), nullable=False),
    sa.Column('isbn', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('submission_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['submission_id'], ['librarian_submission.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('goodreads_import_rows')
