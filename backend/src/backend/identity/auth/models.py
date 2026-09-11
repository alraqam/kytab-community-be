from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, UniqueConstraint, select
from sqlalchemy.orm import column_property

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class User(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a registered user with credentials, role, and avatar."""

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(20), nullable=False, default="user")
    username = Column(String(100), nullable=False, unique=True)
    username_changed_at = Column(DateTime(timezone=True), nullable=True)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    totp_secret = Column(Text, nullable=True)
    is_2fa_enabled = Column(Boolean, nullable=False, default=False)

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

class RecoveryCode(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a single-use two-factor recovery code."""

    __tablename__ = "recovery_codes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    code_hash = Column(Text, nullable=False, unique=True)
    used_at = Column(DateTime(timezone=True), nullable=True)

class OAuthAccount(Base, IntIdMixin, TimeActionMixin):
    """ORM model linking a user to an external OAuth identity provider account."""

    __tablename__ = "oauth_accounts"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False)
    provider_user_id = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_accounts_provider_subject"),
    )

Session.username = column_property(
    select(User.username)
    .where(User.id == Session.user_id)
    .correlate_except(User)
    .scalar_subquery()
)