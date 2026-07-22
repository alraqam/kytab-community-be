
from sqlalchemy import BigInteger, ForeignKey, Column, UniqueConstraint, CheckConstraint

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class Follow(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "follows"

    follower_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    followed_id  = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uq_follower_followed"),
        CheckConstraint("follower_id != followed_id", name="ck_no_self_follow"),
    )