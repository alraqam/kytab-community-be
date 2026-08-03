from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint, String, DateTime, select
from sqlalchemy.orm import column_property

from src.backend.clubs.clubs.models import Club
from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class ClubMembership(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's membership and role in a club."""

    __tablename__ = "club_membership"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, default="member")

    __table_args__ = (
        UniqueConstraint("club_id", "user_id", name="user_club_id"),
    )

class ClubBlocked(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user blocked from a club."""

    __tablename__ = "club_blocked"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("club_id", "user_id", name="block_user_club_id"),
    )

class ClubInvitation(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing an invitation for a user to join a club."""

    __tablename__ = "club_invitation"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    invited_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invited_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    expires_at = Column(DateTime, nullable=False)


class ClubJoinRequest(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a user's request to join a private club."""

    __tablename__ = "club_join_request"

    club_id = Column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    expires_at = Column(DateTime, nullable=False)


ClubMembership.username = column_property(
    select(User.username).where(User.id == ClubMembership.user_id).correlate_except(User).scalar_subquery()
)
ClubMembership.club_name = column_property(
    select(Club.name).where(Club.id == ClubMembership.club_id).correlate_except(Club).scalar_subquery()
)

ClubBlocked.username = column_property(
    select(User.username).where(User.id == ClubBlocked.user_id).correlate_except(User).scalar_subquery()
)
ClubBlocked.club_name = column_property(
    select(Club.name).where(Club.id == ClubBlocked.club_id).correlate_except(Club).scalar_subquery()
)

ClubInvitation.club_name = column_property(
    select(Club.name).where(Club.id == ClubInvitation.club_id).correlate_except(Club).scalar_subquery()
)
ClubInvitation.invited_by_username = column_property(
    select(User.username).where(User.id == ClubInvitation.invited_by_id).correlate_except(User).scalar_subquery()
)
ClubInvitation.invited_user_username = column_property(
    select(User.username).where(User.id == ClubInvitation.invited_user_id).correlate_except(User).scalar_subquery()
)

ClubJoinRequest.club_name = column_property(
    select(Club.name).where(Club.id == ClubJoinRequest.club_id).correlate_except(Club).scalar_subquery()
)
ClubJoinRequest.username = column_property(
    select(User.username).where(User.id == ClubJoinRequest.user_id).correlate_except(User).scalar_subquery()
)
