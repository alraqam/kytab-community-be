from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Text, Boolean

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Review(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "reviews"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=True)
    text = Column(Text, nullable=True)
    contains_spoiler = Column(Boolean, default=False)
