
from sqlalchemy import Column, BigInteger, ForeignKey, Date, String, UniqueConstraint, Boolean, DateTime

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base

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


