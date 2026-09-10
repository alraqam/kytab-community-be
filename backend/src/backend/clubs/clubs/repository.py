from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.filters import ClubFilter, ClubPublicFilter
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import ClubTypes



@dataclass
class ClubRepository:
    """Data-access layer for club persistence and queries."""

    session: AsyncSession

    async def create_club(
            self,
            name: str,
            user_id: int,
            description: str | None = None,
    ) -> Club:
        """Inserts a new club.

        Args:
            name: Club name.
            user_id: ID of the user who owns the club.
            description: Club description, or None.

        Returns:
            Newly created Club instance.
        """
        result = Club(
            name=name,
            description=description,
            owner_id=user_id,
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
    ) -> list[Club]:
        """Lists all clubs, optionally filtered and sorted.

        Args:
            filters: ClubFilter to apply, or None for no filtering.

        Returns:
            List of matching Club instances.
        """
        stmt = select(Club)
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


