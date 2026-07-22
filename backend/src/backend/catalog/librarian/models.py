from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, DateTime

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class LibrarianSubmission(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "librarian_submission"

    submitted_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    title = Column(String(512), nullable=False)
    language = Column(String(100), nullable=False)
    author_name = Column(String(512), nullable=False)
    isbn = Column(String(20), nullable=True)
    cover_url = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    reviewed_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    resulting_work_id = Column(BigInteger, ForeignKey("works.id", ondelete="SET NULL"), nullable=True)
