from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class User(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a registered user with credentials, role, and avatar."""

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(20), nullable=False, default="user")
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class Session(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's login session tied to a hashed refresh token."""

    __tablename__ = "sessions"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token_hash = Column(Text, nullable=False, unique=True)
    device_label = Column(String(512), nullable=True)
    ip_address = Column(Text, nullable=True)
    last_active_at = Column(DateTime(timezone=True), default=datetime.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

Session.username = column_property(
    select(User.username)
    .where(User.id == Session.user_id)
    .correlate_except(User)
    .scalar_subquery()
)