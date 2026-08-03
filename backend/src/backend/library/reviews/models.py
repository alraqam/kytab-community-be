from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Text, Boolean, String, UniqueConstraint, Float, \
    func, select
from sqlalchemy.orm import column_property

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class ReviewComment(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's comment on a review."""

    __tablename__ = "review_comments"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(1000), nullable=False)
    is_edited = Column(Boolean, default=False)


class ReviewLike(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's like on a review."""

    __tablename__ = "review_likes"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "review_id", name="uq_user_review_like"),
    )


class Review(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's review of a work, with an optional rating and text."""

    __tablename__ = "reviews"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=True)
    text = Column(Text, nullable=True)
    contains_spoiler = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)

Review.likes_count = column_property(
    select(func.count(ReviewLike.id))
    .where(ReviewLike.review_id == Review.id)
    .correlate_except(ReviewLike)
    .scalar_subquery()
)