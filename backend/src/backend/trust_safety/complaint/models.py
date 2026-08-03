from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class Complaint(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user-submitted moderation report against a review, comment, post, club, or user."""

    __tablename__ = "complaint"

    reporter_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    object_type = Column(String(100), nullable=False)
    object_id = Column(BigInteger, nullable=False)
    category = Column(String(100), nullable=False)
    comment = Column(String(500), nullable=True)
    status = Column(String(100), nullable=False, default="pending")
    resolved_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    is_escalated = Column(Boolean, nullable=False, default=False)

Complaint.reporter_username = column_property(
    select(User.username).where(User.id == Complaint.reporter_id).correlate_except(User).scalar_subquery()
)
Complaint.resolved_by_username = column_property(
    select(User.username).where(User.id == Complaint.resolved_by_id).correlate_except(User).scalar_subquery()
)
