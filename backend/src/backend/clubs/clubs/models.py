from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base


class Club(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "clubs"

    name = Column(String(256), nullable=False)
    description = Column(String(1024), nullable=True)
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_type = Column(String(20), nullable=False, default="public")
    cover = Column(Text, nullable=True)
    language = Column(String(20), nullable=True)
    is_archived = Column(Boolean, default=False)

    members = relationship("ClubMembership", backref="club", lazy="selectin")

class ClubGenre (Base, IntIdMixin):
    __tablename__ = "club_genre"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(BigInteger, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("club_id", "genre_id",  name="uq_club_genre"),
    )