from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies import get_club_blocked_manager, get_club_blocked_or_404
from src.backend.clubs.club_membership.managers.block import ClubBlockedManager
from src.backend.clubs.club_membership.models import ClubBlocked
from src.backend.clubs.club_membership.schemas import GetBlockedMember, CreateBlockedMember
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User


router = APIRouter(
    prefix="/{club_id}/block",
    tags=["blocks"]
)

@cbv(router)
class ClubBlockedRouter:
    manager: ClubBlockedManager = Depends(get_club_blocked_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.post(
        "/",
        summary="blocking user",
        response_model=GetBlockedMember,
    )
    async def block_user(
            self,
            request: CreateBlockedMember
    ):
        result = await self.manager.block_user(self.user, self.club, request)
        return result

    @router.delete(
        "/",
        summary="deleting block/unblocking user",
    )
    async def delete_block(
            self,
            block: ClubBlocked = Depends(get_club_blocked_or_404)
    ):
        await self.manager.delete_block(self.user, self.club, block)

    @router.get(
        "/",
        summary="getting club's blocked",
        response_model=list[GetBlockedMember],
    )
    async def get_club_blocked(
            self,
    ):
        result = await self.manager.get_club_blocked(self.club)
        return result
