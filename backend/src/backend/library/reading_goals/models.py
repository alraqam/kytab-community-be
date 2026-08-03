from sqlalchemy import BigInteger, ForeignKey, Column, UniqueConstraint, CheckConstraint, Integer, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User

class ReadingGoal(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's book-count reading goal for a given year."""

    __tablename__ = "reading_goals"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    year  = Column(Integer, nullable=False)
    target_count = Column(Integer, nullable=False)


    __table_args__ = (
        UniqueConstraint("user_id", "year", name="uq_user_year"),
    )

ReadingGoal.username = column_property(
    select(User.username).where(User.id == ReadingGoal.user_id).correlate_except(User).scalar_subquery()
)