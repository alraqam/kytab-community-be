from dataclasses import dataclass

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.filters.club import ClubFilter, ClubPublicFilter
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.schemas.club import ClubTypes
from src.backend.identity.auth.models.auth import User
from src.backend.identity.auth.schemas.auth import UserRoleEnum



@dataclass
class ClubRepository:
    """Data-access layer for club persistence and queries."""

    session: AsyncSession

    async def create_club(
            self,
            name: str,
            user_id: int,
            description: str | None = None,
            opening_reason: str | None = None,
    ) -> Club:
        """Inserts a new club.

        Args:
            name: Club name.
            user_id: ID of the user who owns the club.
            description: Club description, or None.
            opening_reason: Creator's optional reason for opening the club (staff-only), or None.

        Returns:
            Newly created Club instance.
        """
        result = Club(
            name=name,
            description=description,
            owner_id=user_id,
            opening_reason=opening_reason,
        )
        self.session.add(result)
        await self.session.flush()
        return result


    async def update_club(
            self,
            club: Club,
            name: str | None = None,
            description: str | None = None,
            club_type: str | None = None,
            cover: str | None = None,
            language: str | None = None,
            member_cap: int | None = None,
    ) -> None:
        """Updates the given fields of a club, skipping unset ones.

        Args:
            club: Club instance to update.
            name: New name, or None to leave unchanged.
            description: New description, or None to leave unchanged.
            club_type: New club type, or None to leave unchanged.
            cover: New cover URL, or None to leave unchanged.
            language: New language, or None to leave unchanged.
            member_cap: New member cap, or None to leave unchanged.
        """
        updates = {
            "name": name,
            "description": description,
            "club_type": club_type,
            "cover": cover,
            "language": language,
            "member_cap": member_cap,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(club, field, value)
        await self.session.flush()

    async def update_status(
            self,
            club: Club,
            status: bool
    ) -> None:
        """Sets a club's archived flag.

        Args:
            club: Club instance to update.
            status: True to archive, False to unarchive.
        """
        club.is_archived = status
        self.session.add(club)
        await self.session.flush()

    async def get_clubs_list(
            self,
            filters: ClubPublicFilter | None = None,
    ) -> list[Club]:
        """Lists non-secret, non-archived clubs, optionally filtered and sorted.

        Args:
            filters: ClubPublicFilter to apply, or None for no filtering.

        Returns:
            List of matching Club instances.
        """
        stmt = select(Club).where(
            and_(
                Club.club_type != ClubTypes.secret,
                Club.is_archived == False,
            )
        )
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_all_clubs(
            self,
            filters: ClubFilter | None = None,
            platform_manager_id: int | None = None,
    ) -> list[Club]:
        """Lists all clubs, optionally filtered and sorted.

        Args:
            filters: ClubFilter to apply, or None for no filtering.
            platform_manager_id: Restrict to clubs managed by this platform moderator, or None for all clubs.

        Returns:
            List of matching Club instances.
        """
        stmt = select(Club)
        if platform_manager_id is not None:
            stmt = stmt.where(Club.platform_manager_id == platform_manager_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_club_by_id(
            self,
            club_id: int
    ) -> Club | None:
        """Fetches a single club by ID.

        Args:
            club_id: ID of the club to fetch.

        Returns:
            Matching Club instance, or None if not found.
        """
        stmt = select(Club).where(Club.id == club_id)
        result = await self.session.execute(stmt)
        club = result.scalar_one_or_none()
        return club

    async def transfer_ownership(
            self,
            club: Club,
            new_owner_id: int
    ) -> None:
        """Changes the owner of a club.

        Args:
            club: Club instance whose ownership is being transferred.
            new_owner_id: ID of the user becoming the new owner.
        """
        club.owner_id = new_owner_id
        self.session.add(club)
        await self.session.flush()

    async def set_platform_manager(
            self,
            club: Club,
            manager_id: int | None,
    ) -> None:
        """Sets (or clears) the platform moderator responsible for a club.

        Args:
            club: Club instance to update.
            manager_id: ID of the platform moderator, or None to leave the club unassigned.
        """
        club.platform_manager_id = manager_id
        self.session.add(club)
        await self.session.flush()

    async def get_active_clubs_by_manager(
            self,
            manager_id: int,
    ) -> list[Club]:
        """Lists the non-archived clubs assigned to a platform moderator.

        Args:
            manager_id: ID of the platform moderator.

        Returns:
            List of Club instances, oldest first.
        """
        stmt = (
            select(Club)
            .where(Club.platform_manager_id == manager_id, Club.is_archived.isnot(True))
            .order_by(Club.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unassigned_active_clubs(self) -> list[Club]:
        """Lists non-archived clubs that have no platform moderator assigned.

        Returns:
            List of Club instances, oldest first.
        """
        stmt = (
            select(Club)
            .where(Club.platform_manager_id.is_(None), Club.is_archived.isnot(True))
            .order_by(Club.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_platform_manager_loads(self) -> list[tuple[int, str, int]]:
        """Counts the non-archived clubs assigned to each eligible platform moderator.

        Eligible moderators have the `moderator` role, are active, and are not deleted.
        Moderators with no clubs are included with a count of 0.

        Returns:
            List of (manager_id, username, active_club_count) tuples ordered by manager ID.
        """
        stmt = (
            select(User.id, User.username, func.count(Club.id))
            .outerjoin(
                Club,
                and_(Club.platform_manager_id == User.id, Club.is_archived.isnot(True)),
            )
            .where(
                User.role == UserRoleEnum.moderator,
                User.is_active.is_(True),
                User.is_deleted.is_(False),
            )
            .group_by(User.id, User.username)
            .order_by(User.id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]
