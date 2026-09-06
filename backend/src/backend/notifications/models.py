from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, Text, DateTime, UniqueConstraint, select
from sqlalchemy.orm import column_property

from src.backend.clubs.clubs.models import Club
from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class Notification(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a single in-app notification delivered to a user."""

    __tablename__ = "notifications"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    object_type = Column(String(100), nullable=True)
    object_id = Column(BigInteger, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)


class NotificationPreference(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's notification delivery settings for a category, optionally scoped to a club."""

    __tablename__ = "notification_preferences"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True)
    category = Column(String(100), nullable=False)
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    push_enabled = Column(Boolean, nullable=False, default=False)
    digest_frequency = Column(String(100), nullable=False, default="none")
    is_muted = Column(Boolean, nullable=False, default=False)
    last_digest_sent_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "club_id", "category", name="uq_user_club_category_preference"),
    )


class PushSubscription(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a browser's Web Push subscription for a user."""

    __tablename__ = "push_subscriptions"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)


Notification.username = column_property(
    select(User.username).where(User.id == Notification.user_id).correlate_except(User).scalar_subquery()
)
Notification.club_name = column_property(
    select(Club.name).where(Club.id == Notification.club_id).correlate_except(Club).scalar_subquery()
)

NotificationPreference.username = column_property(
    select(User.username).where(User.id == NotificationPreference.user_id).correlate_except(User).scalar_subquery()
)
NotificationPreference.club_name = column_property(
    select(Club.name).where(Club.id == NotificationPreference.club_id).correlate_except(Club).scalar_subquery()
)
