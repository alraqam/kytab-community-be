from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint, Integer, Text, DateTime, String, select
from sqlalchemy.orm import column_property

from src.backend.catalog.books.models import Work
from src.backend.clubs.clubs.models import Club
from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class VotingPoll(Base, IntIdMixin, TimeActionMixin):
    """ORM model for a club's voting poll used to choose the next book."""

    __tablename__ = "voting_polls"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    closes_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="active")

class PollCandidate(Base, IntIdMixin):
    """ORM model representing a book nominated as a candidate in a voting poll."""

    __tablename__ = "poll_candidates"

    poll_id = Column(BigInteger, ForeignKey("voting_polls.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("poll_id", "work_id", name="poll_work_id"),
    )

class PollVote(Base, IntIdMixin, TimeActionMixin):
    """ORM model recording a single user's vote for a candidate in a poll."""

    __tablename__ = "poll_votes"

    poll_id = Column(BigInteger, ForeignKey("voting_polls.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(BigInteger, ForeignKey("poll_candidates.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("poll_id", "user_id", name="poll_user_id"),
    )

VotingPoll.club_name = column_property(
    select(Club.name).where(Club.id == VotingPoll.club_id).correlate_except(Club).scalar_subquery()
)
VotingPoll.created_by_username = column_property(
    select(User.username).where(User.id == VotingPoll.created_by_id).correlate_except(User).scalar_subquery()
)

PollCandidate.work_title = column_property(
    select(Work.canonical_title).where(Work.id == PollCandidate.work_id).correlate_except(Work).scalar_subquery()
)

PollVote.username = column_property(
    select(User.username).where(User.id == PollVote.user_id).correlate_except(User).scalar_subquery()
)