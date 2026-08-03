from sqlalchemy import Column, String, Text, Integer, Boolean, BigInteger, ForeignKey, UniqueConstraint, and_, select
from sqlalchemy.orm import column_property, relationship

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Work(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing an abstract literary work, independent of any specific edition."""

    __tablename__ = "works"

    canonical_title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    primary_language = Column(String(100), nullable=True)

    authors = relationship("Author", secondary="work_author", order_by="WorkAuthor.order", lazy="selectin", viewonly=True)
    genres = relationship("Genre", secondary="work_genre", lazy="selectin", viewonly=True)
    series = relationship("Series", secondary="work_series", lazy="selectin", viewonly=True)


class Edition(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a specific published edition of a Work (e.g. a particular publisher/printing)."""

    __tablename__ = "editions"

    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(512), nullable=False)
    language = Column(String(100), nullable=False)
    publisher = Column(String(512), nullable=True)
    published_year = Column(Integer, nullable=True)
    pages_count = Column(Integer, nullable=True)
    isbn = Column(String(20), nullable=True)
    cover_url = Column(Text, nullable=True)
    google_books_id = Column(String(512), nullable=False, unique=True)
    open_library_id = Column(String(512), nullable=False, unique=True)
    is_primary = Column(Boolean, nullable=False, default=False)

Work.cover_url = column_property(
    select(Edition.cover_url)
    .where(and_(Edition.work_id == Work.id, Edition.is_primary == True))
    .correlate_except(Edition)
    .scalar_subquery()
)

Edition.work_title = column_property(
    select(Work.canonical_title)
    .where(Work.id == Edition.work_id)
    .correlate_except(Work)
    .scalar_subquery()
)


class Author(Base, IntIdMixin):
    """ORM model representing a book author."""

    __tablename__ = "authors"

    name = Column(String(512), nullable=False)
    bio = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)

class WorkAuthor(Base, IntIdMixin):
    """ORM model linking an Author to a Work, with an optional display order."""

    __tablename__ = "work_author"

    author_id = Column(BigInteger, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("author_id", "work_id",  name="uq_work_author"),
    )


class Series(Base, IntIdMixin):
    """ORM model representing a book series."""

    __tablename__ = "series"

    name = Column(String(512), nullable=False)

class WorkSeries(Base, IntIdMixin):
    """ORM model linking a Work to a Series, with an optional sequence number."""

    __tablename__ = "work_series"

    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    series_id = Column(BigInteger, ForeignKey("series.id", ondelete="CASCADE"), nullable=False)
    sequence_number = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("work_id", "series_id",  name="uq_work_series"),
    )


class Genre(Base, IntIdMixin):
    """ORM model representing a book genre/category."""

    __tablename__ = "genres"

    name = Column(String(512), nullable=False)
    slug  = Column(Text, nullable=False)

class WorkGenre (Base, IntIdMixin):
    """ORM model linking a Work to a Genre."""

    __tablename__ = "work_genre"

    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(BigInteger, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("work_id", "genre_id",  name="uq_work_genre"),
    )


