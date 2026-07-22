from sqlalchemy import String, Column, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class Profile(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "profiles"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fullname = Column(String(512), nullable=False)
    avatar = Column(Text, nullable=True)
    bio = Column(String(1024), nullable=True)
    favorite_genres = Column(JSONB, nullable=True)
    links = Column(JSONB, nullable=True)
    visibility = Column(String(20), nullable=False, default="public")