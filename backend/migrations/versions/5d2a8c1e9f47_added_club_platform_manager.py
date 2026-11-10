"""added_club_platform_manager

Revision ID: 5d2a8c1e9f47
Revises: 3b7e1d9c4a52
Create Date: 2026-11-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d2a8c1e9f47'
down_revision: Union[str, Sequence[str], None] = '3b7e1d9c4a52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('clubs', sa.Column('platform_manager_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        'fk_clubs_platform_manager_id_users',
        'clubs', 'users',
        ['platform_manager_id'], ['id'],
        ondelete='SET NULL',
    )
    op.create_index(op.f('ix_clubs_platform_manager_id'), 'clubs', ['platform_manager_id'], unique=False)

    # Backfill: spread existing active clubs evenly (round-robin, oldest club first)
    # across active platform moderators. With no moderators, clubs stay unassigned.
    bind = op.get_bind()
    manager_ids = [
        row[0] for row in bind.execute(sa.text(
            "SELECT id FROM users "
            "WHERE role = 'moderator' AND is_active IS TRUE AND is_deleted IS FALSE "
            "ORDER BY id"
        ))
    ]
    if not manager_ids:
        return
    club_ids = [
        row[0] for row in bind.execute(sa.text(
            "SELECT id FROM clubs WHERE is_archived IS NOT TRUE ORDER BY id"
        ))
    ]
    for index, club_id in enumerate(club_ids):
        bind.execute(
            sa.text("UPDATE clubs SET platform_manager_id = :manager_id WHERE id = :club_id"),
            {"manager_id": manager_ids[index % len(manager_ids)], "club_id": club_id},
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_clubs_platform_manager_id'), table_name='clubs')
    op.drop_constraint('fk_clubs_platform_manager_id_users', 'clubs', type_='foreignkey')
    op.drop_column('clubs', 'platform_manager_id')
