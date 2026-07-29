from sqlalchemy import Column, BigInteger, ForeignKey, String, Date, DateTime, Integer, Boolean, UniqueConstraint

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Thread(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "threads"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True)
    milestone_id = Column(BigInteger, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=True)
    is_general = Column(Boolean, default=False)
    title = Column(String(100), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_locked = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)