from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.blocked_users.dependencies import get_blocked_user_manager, get_blocked_user_or_404
from src.backend.identity.blocked_users.managers import BlockedUserManager
from src.backend.identity.blocked_users.models import BlockedUser
from src.backend.identity.blocked_users.schemas import GetBlocked, CreateBlock

router = APIRouter(
    prefix="/block",
    tags=["blocks"]
)

@cbv(router)
class BlockedUserRouter:
    manager: BlockedUserManager = Depends(get_blocked_user_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="blocking user",
        response_model=GetBlocked,
    )
    async def block_user(
            self,
            request: CreateBlock
    ):
        result = await self.manager.block_user(self.user, request)
        return result

    @router.delete(
        "/",
        summary="deleting block/unblocking user",
    )
    async def delete_block(
            self,
            block: BlockedUser = Depends(get_blocked_user_or_404)
    ):
        await self.manager.delete_block(self.user, block)

    @router.get(
        "/",
        summary="getting user's blocked",
        response_model=list[GetBlocked],
    )
    async def get_user_blocked(
            self,
    ):
        result = await self.manager.get_user_blocked(self.user)
        return result
