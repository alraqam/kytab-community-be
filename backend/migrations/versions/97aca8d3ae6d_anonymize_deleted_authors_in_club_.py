"""anonymize_deleted_authors_in_club_posts

Revision ID: 97aca8d3ae6d
Revises: f44e1d6dab2b
Create Date: 2026-09-12 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97aca8d3ae6d'
down_revision: Union[str, Sequence[str], None] = 'f44e1d6dab2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('threads', 'created_by_id', nullable=True)
    op.drop_constraint('threads_created_by_id_fkey', 'threads', type_='foreignkey')
    op.create_foreign_key('threads_created_by_id_fkey', 'threads', 'users', ['created_by_id'], ['id'], ondelete='SET NULL')

    op.alter_column('posts', 'author_id', nullable=True)
    op.drop_constraint('posts_author_id_fkey', 'posts', type_='foreignkey')
    op.create_foreign_key('posts_author_id_fkey', 'posts', 'users', ['author_id'], ['id'], ondelete='SET NULL')

    op.alter_column('post_reactions', 'user_id', nullable=True)
    op.drop_constraint('post_reactions_user_id_fkey', 'post_reactions', type_='foreignkey')
    op.create_foreign_key('post_reactions_user_id_fkey', 'post_reactions', 'users', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('post_reactions_user_id_fkey', 'post_reactions', type_='foreignkey')
    op.create_foreign_key('post_reactions_user_id_fkey', 'post_reactions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('post_reactions', 'user_id', nullable=False)

    op.drop_constraint('posts_author_id_fkey', 'posts', type_='foreignkey')
    op.create_foreign_key('posts_author_id_fkey', 'posts', 'users', ['author_id'], ['id'], ondelete='CASCADE')
    op.alter_column('posts', 'author_id', nullable=False)

    op.drop_constraint('threads_created_by_id_fkey', 'threads', type_='foreignkey')
    op.create_foreign_key('threads_created_by_id_fkey', 'threads', 'users', ['created_by_id'], ['id'], ondelete='CASCADE')
    op.alter_column('threads', 'created_by_id', nullable=False)
