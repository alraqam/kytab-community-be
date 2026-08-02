from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, Text, UniqueConstraint

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class Notification(Base, IntIdMixin, TimeActionMixin):
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
    __tablename__ = "notification_preferences"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True)
    category = Column(String(100), nullable=False)
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    push_enabled = Column(Boolean, nullable=False, default=False)
    digest_frequency = Column(String(100), nullable=False, default="none")
    is_muted = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "club_id", "category", name="uq_user_club_category_preference"),
    )
