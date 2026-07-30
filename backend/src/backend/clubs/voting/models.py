from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint, Integer, Text, DateTime, String

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


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