from sqlalchemy import Column, BigInteger, ForeignKey, String, Date, DateTime, Integer, Boolean, UniqueConstraint

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class ReadingSession(Base, IntIdMixin, TimeActionMixin):
    """ORM model for a club's reading session tied to a specific book and deadline."""

    __tablename__ = "reading_sessions"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="active")
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, nullable=True)

class Milestone(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "milestones"

    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(255), nullable=False, default="active")
    boundary_type = Column(String(20), nullable=False, default="active")
    boundary_value = Column(BigInteger, nullable=False)
    target_date = Column(Date, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

class MilestoneProgress(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "milestone_progress"

    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_finished = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "session_id", name="uq_session_user"),
    )


