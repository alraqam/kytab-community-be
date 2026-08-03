from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint, String, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class ClubEvent(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a scheduled event hosted by a club."""

    __tablename__ = "events"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), nullable=False)
    location_text = Column(String(100), nullable=True)
    meeting_url = Column(String(100), nullable=True)

class EventRSVP(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's RSVP response to a club event."""

    __tablename__ = "event_rsvps"

    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user"),
    )

ClubEvent.created_by_username = column_property(
    select(User.username).where(User.id == ClubEvent.created_by_id).correlate_except(User).scalar_subquery()
)

EventRSVP.username = column_property(
    select(User.username).where(User.id == EventRSVP.user_id).correlate_except(User).scalar_subquery()
)