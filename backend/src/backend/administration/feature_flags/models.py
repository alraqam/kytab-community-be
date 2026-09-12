from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Boolean, Integer, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class FeatureFlag(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a feature flag used for staged rollouts."""

    __tablename__ = "feature_flags"

    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=False)
    rollout_percentage = Column(Integer, nullable=False, default=100)

FeatureFlag.created_by_username = column_property(
    select(User.username).where(User.id == FeatureFlag.created_by_id).correlate_except(User).scalar_subquery()
)
