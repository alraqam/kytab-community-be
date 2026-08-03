
from sqlalchemy import Column, BigInteger, ForeignKey, Date, String, UniqueConstraint, Boolean, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.catalog.books.models import Edition, Work
from src.backend.core.models import IntIdMixin, TimeActionMixin, Base
from src.backend.identity.auth.models import User

class Shelf(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user-owned bookshelf, either default or custom-named."""

    __tablename__ = "shelves"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    is_default = Column(Boolean, nullable=True)
    visibility = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_shelf_user_name"),
    )


class ShelfItem(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a work (and optionally a specific edition) placed on a shelf."""

    __tablename__ = "shelf_items"

    shelf_id = Column(BigInteger, ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(BigInteger, ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    edition_id = Column(BigInteger, ForeignKey("editions.id", ondelete="CASCADE"), nullable=True)


    __table_args__ = (
        UniqueConstraint("shelf_id", "work_id", name="uq_shelf_work"),
    )

Shelf.username = column_property(
    select(User.username).where(User.id == Shelf.user_id).correlate_except(User).scalar_subquery()
)

ShelfItem.work_title = column_property(
    select(Work.canonical_title).where(Work.id == ShelfItem.work_id).correlate_except(Work).scalar_subquery()
)
ShelfItem.edition_title = column_property(
    select(Edition.title).where(Edition.id == ShelfItem.edition_id).correlate_except(Edition).scalar_subquery()
)


