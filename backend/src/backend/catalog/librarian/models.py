from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.catalog.books.models import Work
from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class LibrarianSubmission(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user-submitted book proposal awaiting librarian review."""

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

LibrarianSubmission.submitted_by_username = column_property(
    select(User.username)
    .where(User.id == LibrarianSubmission.submitted_by_id)
    .correlate_except(User)
    .scalar_subquery()
)

LibrarianSubmission.reviewed_by_username = column_property(
    select(User.username)
    .where(User.id == LibrarianSubmission.reviewed_by_id)
    .correlate_except(User)
    .scalar_subquery()
)

LibrarianSubmission.resulting_work_title = column_property(
    select(Work.canonical_title)
    .where(Work.id == LibrarianSubmission.resulting_work_id)
    .correlate_except(Work)
    .scalar_subquery()
)
