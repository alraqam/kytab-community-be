from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Boolean, Integer, UniqueConstraint, select
from sqlalchemy.orm import relationship, column_property

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base
from src.backend.identity.auth.models import User

DEFAULT_CLUB_MEMBER_CAP = 150

class Club(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a book club, its ownership, and its visibility settings."""

    __tablename__ = "clubs"

    name = Column(String(256), nullable=False)
    description = Column(String(1024), nullable=True)
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_type = Column(String(20), nullable=False, default="private")
    cover = Column(Text, nullable=True)
    language = Column(String(20), nullable=True)
    is_archived = Column(Boolean, default=False)
    member_cap = Column(Integer, nullable=False, default=DEFAULT_CLUB_MEMBER_CAP)

    members = relationship("ClubMembership", backref="club", lazy="selectin")
    events = relationship("ClubEvent", backref="club", lazy="selectin")
    genres = relationship("Genre", secondary="club_genre", lazy="selectin", viewonly=True)

Club.owner_username = column_property(
    select(User.username).where(User.id == Club.owner_id).correlate_except(User).scalar_subquery()
)

class ClubGenre (Base, IntIdMixin):
    """ORM model representing the association between a club and one of its genres."""

    __tablename__ = "club_genre"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(BigInteger, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("club_id", "genre_id",  name="uq_club_genre"),
    )