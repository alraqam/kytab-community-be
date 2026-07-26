from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Text, Boolean, String, UniqueConstraint, Float

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Review(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "reviews"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=True)
    text = Column(Text, nullable=True)
    contains_spoiler = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)


class ReviewComment(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "review_comments"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(1000), nullable=False)
    is_edited = Column(Boolean, default=False)


class ReviewLike(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "review_likes"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "review_id", name="uq_user_review_like"),
    )
