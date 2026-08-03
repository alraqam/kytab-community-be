from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Boolean, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class Announcement(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a site-wide administrative announcement."""

    __tablename__ = "announcements"

    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    published_at = Column(DateTime, nullable=True)

Announcement.created_by_username = column_property(
    select(User.username).where(User.id == Announcement.created_by_id).correlate_except(User).scalar_subquery()
)
