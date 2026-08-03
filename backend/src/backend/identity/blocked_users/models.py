from sqlalchemy import Column, ForeignKey, BigInteger, UniqueConstraint, CheckConstraint, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class BlockedUser(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing one user blocking another, preventing self-blocks and duplicate blocks."""

    __tablename__ = "blocked_users"

    blocker_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_blocker_blocked"),
        CheckConstraint("blocker_id != blocked_id", name="ck_no_self_block"),
    )

BlockedUser.blocker_username = column_property(
    select(User.username).where(User.id == BlockedUser.blocker_id).correlate_except(User).scalar_subquery()
)
BlockedUser.blocked_username = column_property(
    select(User.username).where(User.id == BlockedUser.blocked_id).correlate_except(User).scalar_subquery()
)