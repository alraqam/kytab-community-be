
from sqlalchemy import Column, BigInteger, ForeignKey, String

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class GoodreadsImportRow(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a Goodreads CSV row that matched no catalog entry."""

    __tablename__ = "goodreads_import_rows"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(512), nullable=False)
    author_name = Column(String(512), nullable=False)
    isbn = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default="unmatched")
    submission_id = Column(BigInteger, ForeignKey("librarian_submission.id", ondelete="SET NULL"), nullable=True)
