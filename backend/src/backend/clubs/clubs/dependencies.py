from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.exceptions import IsNotClubOwnerError
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User
from src.backend.core.dependencies import get_db

def is_club_owner(
        club: Club,
        user: User,
) -> User:
    if user.id != club.owner_id:
        raise IsNotClubOwnerError("Is not club owner")
    return user

from src.backend.clubs.clubs.managers import ClubManager

async def get_club_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubManager:
    return ClubManager(session)

async def get_club_or_404(
        club_id: int,
        manager: ClubManager = Depends(get_club_manager)
) -> Club:
    return await manager.get_club_by_id(club_id)