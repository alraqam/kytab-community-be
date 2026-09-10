from dataclasses import dataclass
from typing import Tuple

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.filters import ClubMembersFilter
from src.backend.clubs.club_membership.models import ClubMembership
from src.backend.clubs.club_membership.schemas import MemberRole
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User


@dataclass
class ClubMembershipRepository:
    """Data-access layer for ClubMembership model operations."""

    session: AsyncSession

    async def create_membership(
            self,
            club_id: int,
            user_id: int,
            role: str
    ) -> ClubMembership:
        """Inserts a new club membership record.

        Args:
            club_id: ID of the club.
            user_id: ID of the user joining.
            role: Role to assign to the new member.

        Returns:
            Newly created ClubMembership instance.
        """
        result = ClubMembership(
            club_id=club_id,
            user_id=user_id,
            role=role,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def change_member_role(
            self,
            membership: ClubMembership,
            role: MemberRole
    ) -> None:
        """Updates the role on a membership record.

        Args:
            membership: ClubMembership instance to update.
            role: New MemberRole value.
        """
        membership.role = role
        self.session.add(membership)
        await self.session.flush()

    async def delete_membership(
            self,
            membership: ClubMembership,
    ) -> None:
        """Deletes the membership record and flushes the session.

        Args:
            membership: ClubMembership instance to delete.
        """
        await self.session.delete(membership)
        await self.session.flush()

    async def get_user_club_membership(
            self,
            club: Club,
            user: User
    ) -> ClubMembership | None:
        """Fetches the membership record for a specific user in a specific club.

        Args:
            club: Club to check membership in.
            user: User to look up.

        Returns:
            ClubMembership instance if found, None otherwise.
        """
        stmt = select(ClubMembership).where(
            and_(
                ClubMembership.club_id == club.id,
                ClubMembership.user_id == user.id,
            )
        )
        result = await self.session.execute(stmt)
        membership = result.scalar_one_or_none()
        return membership

    async def count_memberships(
            self,
            club_id: int,
    ) -> int:
        """Counts the current members of a club.

        Args:
            club_id: ID of the club to count members for.

        Returns:
            Number of membership records for the club.
        """
        stmt = select(func.count()).select_from(ClubMembership).where(ClubMembership.club_id == club_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_memberships(
            self,
            club: Club,
            filters: ClubMembersFilter | None = None,
    ) -> list[ClubMembership]:
        """Returns all membership records for a club with optional filtering.

        Args:
            club: Club whose members are queried.
            filters: Optional ClubMembersFilter for filtering and sorting.

        Returns:
            List of ClubMembership instances.
        """
        stmt = select(ClubMembership).where(ClubMembership.club_id == club.id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def get_user_memberships(
            self,
            user: User
    ) -> list[ClubMembership]:
        """Returns all club memberships for the given user.

        Args:
            user: User whose memberships are retrieved.

        Returns:
            List of ClubMembership instances across all clubs.
        """
        stmt = select(ClubMembership).where(ClubMembership.user_id == user.id)

        result = await self.session.execute(stmt)
        memberships = result.scalars().all()
        return memberships


    async def get_memberships_for_users(
            self,
            user_ids: list[int],
    ) -> list[ClubMembership]:
        """Returns all club memberships for any of the given users.

        Args:
            user_ids: IDs of the users whose memberships are retrieved.

        Returns:
            List of ClubMembership instances across all clubs.
        """
        stmt = select(ClubMembership).where(ClubMembership.user_id.in_(user_ids))
        result = await self.session.execute(stmt)
        memberships = result.scalars().all()
        return memberships

    async def get_club_owner_moderator(
            self,
            club: Club
    ) -> list[ClubMembership]:
        """Returns club's owner and moderators for the given club.

        Args:
            club: Club whose memberships are retrieved.

        Returns:
            List of ClubMembership instances across all clubs.
        """
        stmt = select(ClubMembership).where(
            and_(
                ClubMembership.club_id == club.id,
                ClubMembership.role.in_([MemberRole.club_moderator, MemberRole.club_owner])
            )
        )
        result = await self.session.execute(stmt)
        memberships = result.scalars().all()
        return memberships