from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, Boolean, UniqueConstraint, select
from sqlalchemy.orm import column_property

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base
from src.backend.identity.auth.models import User


class Thread(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a discussion thread, either club-general or scoped to a reading session milestone."""

    __tablename__ = "threads"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=True)
    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=True)
    is_general = Column(Boolean, default=False)
    title = Column(String(100), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_locked = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)


class Post(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a single post within a discussion thread, optionally a reply to another post."""

    __tablename__ = "posts"

    thread_id = Column(BigInteger, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    parent_post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    author_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(100), nullable=False)
    body = Column(String(512), nullable=False)
    is_spoiler = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

class PostReaction(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's emoji reaction to a post."""

    __tablename__ = "post_reactions"

    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    emoji = Column(String(30), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id",  "post_id", "emoji", name="uq_user_post_emoji"),
    )

Thread.created_by_username = column_property(
    select(User.username).where(User.id == Thread.created_by_id).correlate_except(User).scalar_subquery()
)

Post.author_username = column_property(
    select(User.username).where(User.id == Post.author_id).correlate_except(User).scalar_subquery()
)

Post.thread_title = column_property(
    select(Thread.title).where(Thread.id == Post.thread_id).correlate_except(Thread).scalar_subquery()
)

PostReaction.username = column_property(
    select(User.username).where(User.id == PostReaction.user_id).correlate_except(User).scalar_subquery()
)

