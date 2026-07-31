from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, Boolean, UniqueConstraint

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Thread(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "threads"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=True)
    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=True)
    is_general = Column(Boolean, default=False)
    title = Column(String(100), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_locked = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)


class Post(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "posts"

    thread_id = Column(BigInteger, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    parent_post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    author_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    body = Column(String(512), nullable=False)
    is_spoiler = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

class PostReaction(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "post_reactions"

    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emoji = Column(String(30), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id",  "post_id", "emoji", name="uq_user_post_emoji"),
    )

