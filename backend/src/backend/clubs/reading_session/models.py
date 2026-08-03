from sqlalchemy import Column, BigInteger, ForeignKey, String, Date, DateTime, Integer, Boolean, UniqueConstraint, select
from sqlalchemy.orm import column_property

from src.backend.catalog.books.models import Work
from src.backend.clubs.clubs.models import Club
from src.backend.core.models import IntIdMixin, TimeActionMixin, Base
from src.backend.identity.auth.models import User


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
    """ORM model for a reading progress checkpoint within a reading session."""

    __tablename__ = "milestones"

    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(255), nullable=False, default="active")
    boundary_type = Column(String(20), nullable=False, default="active")
    boundary_value = Column(BigInteger, nullable=False)
    target_date = Column(Date, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

class MilestoneProgress(Base, IntIdMixin, TimeActionMixin):
    """ORM model tracking a single user's progress toward a milestone in a reading session."""

    __tablename__ = "milestone_progress"

    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_finished = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "session_id", name="uq_session_user"),
    )

class DiscussionPrompt(Base, IntIdMixin, TimeActionMixin):
    """ORM model for a discussion question attached to a reading session milestone."""

    __tablename__ = "discussion_prompts"

    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(512), nullable=False)

ReadingSession.club_name = column_property(
    select(Club.name).where(Club.id == ReadingSession.club_id).correlate_except(Club).scalar_subquery()
)
ReadingSession.work_title = column_property(
    select(Work.canonical_title).where(Work.id == ReadingSession.work_id).correlate_except(Work).scalar_subquery()
)
ReadingSession.created_by_username = column_property(
    select(User.username).where(User.id == ReadingSession.created_by_id).correlate_except(User).scalar_subquery()
)

MilestoneProgress.username = column_property(
    select(User.username).where(User.id == MilestoneProgress.user_id).correlate_except(User).scalar_subquery()
)
MilestoneProgress.milestone_label = column_property(
    select(Milestone.label).where(Milestone.id == MilestoneProgress.milestone_id).correlate_except(Milestone).scalar_subquery()
)

DiscussionPrompt.milestone_label = column_property(
    select(Milestone.label).where(Milestone.id == DiscussionPrompt.milestone_id).correlate_except(Milestone).scalar_subquery()
)
DiscussionPrompt.created_by_username = column_property(
    select(User.username).where(User.id == DiscussionPrompt.created_by_id).correlate_except(User).scalar_subquery()
)


