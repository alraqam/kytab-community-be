from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, DateTime

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class Complaint(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "complaint"

    reporter_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    object_type = Column(String(100), nullable=False)
    object_id = Column(BigInteger, nullable=False)
    category = Column(String(100), nullable=False)
    comment = Column(String(500), nullable=True)
    status = Column(String(100), nullable=False, default="pending")
    resolved_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
