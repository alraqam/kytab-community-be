from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.identity.blocked_users.dependencies.blocked_user import get_blocked_user_manager, get_blocked_user_or_404
from src.backend.identity.blocked_users.managers.blocked_user import BlockedUserManager
from src.backend.identity.blocked_users.models.blocked_user import BlockedUser
from src.backend.identity.blocked_users.schemas.blocked_user import GetBlocked, CreateBlock
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/block",
    tags=["blocks"]
)

@cbv(router)
class BlockedUserRouter:
    """CBV router for managing user blocks: blocking, unblocking, and listing."""

    manager: BlockedUserManager = Depends(get_blocked_user_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="blocking user",
        response_model=GetBlocked,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 409),
    )
    async def block_user(
            self,
            request: CreateBlock
    ):
        """Blocks another user on behalf of the current user."""
        result = await self.manager.block_user(self.user, request)
        return result

    @router.delete(
        "/",
        summary="deleting block/unblocking user",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_block(
            self,
            block: BlockedUser = Depends(get_blocked_user_or_404)
    ):
        """Removes a block, unblocking the target user."""
        await self.manager.delete_block(self.user, block)

    @router.get(
        "/",
        summary="getting user's blocked",
        response_model=list[GetBlocked],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_blocked(
            self,
    ):
        """Lists the users blocked by the current user."""
        result = await self.manager.get_user_blocked(self.user)
        return result
