from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.follow.dependencies import get_follow_manager, get_follow_or_404
from src.backend.identity.follow.managers import FollowManager
from src.backend.identity.follow.models import Follow
from src.backend.identity.follow.schemas import GetFollow, CreateFollow

router = APIRouter(
    prefix="/follow",
    tags=["follows"]
)

@cbv(router)
class FollowRouter:
    manager: FollowManager = Depends(get_follow_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="following user",
        response_model=GetFollow,
    )
    async def follow_user(
            self,
            request: CreateFollow
    ):
        result = await self.manager.follow_user(self.user, request)
        return result

    @router.delete(
        "/",
        summary="unfollowing user",
    )
    async def unfollow(
            self,
            follow: Follow = Depends(get_follow_or_404)
    ):
        await self.manager.unfollow(self.user, follow)

    @router.get(
        "/followers",
        summary="getting user's followers",
        response_model=list[GetFollow],
    )
    async def get_user_followers(
            self,
    ):
        result = await self.manager.get_user_followers(self.user)
        return result

    @router.get(
        "/followings",
        summary="getting user's followings",
        response_model=list[GetFollow],
    )
    async def get_user_followings(
            self,
    ):
        result = await self.manager.get_user_followings(self.user)
        return result
