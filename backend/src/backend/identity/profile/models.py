from sqlalchemy import String, Column, Text, BigInteger, ForeignKey, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class Profile(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's public profile information."""

    __tablename__ = "profiles"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fullname = Column(String(512), nullable=False)
    avatar = Column(Text, nullable=True)
    bio = Column(String(1024), nullable=True)
    favorite_genres = Column(JSONB, nullable=True)
    links = Column(JSONB, nullable=True)
    visibility = Column(String(20), nullable=False, default="public")

Profile.username = column_property(
    select(User.username)
    .where(User.id == Profile.user_id)
    .correlate_except(User)
    .scalar_subquery()
)