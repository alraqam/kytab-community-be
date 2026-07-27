from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.filters import ClubFilter, ClubPublicFilter
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import ClubTypes



@dataclass
class ClubRepository:
    session: AsyncSession

    async def create_club(
            self,
            name: str,
            user_id: int,
            description: str | None = None,
    ) -> Club:
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
    ) -> None:
        updates = {
            "name": name,
            "description": description,
            "club_type": club_type,
            "cover": cover,
            "language": language,
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
        club.is_archived = status
        self.session.add(club)
        await self.session.flush()

    async def get_clubs_list(
            self,
            filters: ClubPublicFilter | None = None,
    ) -> list[Club]:
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
        stmt = select(Club).where(Club.id == club_id)
        result = await self.session.execute(stmt)
        club = result.scalar_one_or_none()
        return club

    async def transfer_ownership(
            self,
            club: Club,
            new_owner_id: int
    ) -> None:
        club.owner_id = new_owner_id
        self.session.add(club)
        await self.session.flush()


