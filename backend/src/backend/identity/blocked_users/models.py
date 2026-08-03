from sqlalchemy import Column, ForeignKey, BigInteger, UniqueConstraint, CheckConstraint

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class BlockedUser(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing one user blocking another, preventing self-blocks and duplicate blocks."""

    __tablename__ = "blocked_users"

    blocker_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_blocker_blocked"),
        CheckConstraint("blocker_id != blocked_id", name="ck_no_self_block"),
    )