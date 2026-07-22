from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.profile.dependencies import get_profile_manager
from src.backend.identity.profile.managers import ProfileManager
from src.backend.identity.profile.schemas import UpdateProfileAvatar, UpdateProfile, UpdateProfileVisibility, GetProfile
from src.backend.identity.users.dependencies import get_user_or_404

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@cbv(router)
class ProfileRouter:
    """CBV router for authenticated user profile endpoints."""

    manager: ProfileManager = Depends(get_profile_manager)
    user: User = Depends(get_current_user)

    @router.put(
        "/{user_id}/avatar",
        summary="updating avatar"
    )
    async def update_avatar(
            self,
            request: UpdateProfileAvatar,
    ):
        """Updates the current user's avatar URL.

        Args:
            request: UpdateUserAvatar payload with the new avatar_url.
        """
        await self.manager.update_avatar(self.user, request)

    @router.put(
        "/{user_id}/profile",
        summary="updating profile"
    )
    async def update_profile(
            self,
            request: UpdateProfile,
    ):
        await self.manager.update_profile(self.user, request)

    @router.put(
        "/{user_id}/visibility",
        summary="updating visibility"
    )
    async def update_visibility(
            self,
            request: UpdateProfileVisibility,
    ):
        await self.manager.update_visibility(self.user, request)

    @router.get(
        "/my-profile",
        summary="getting current user's profile",
        response_model=GetProfile
    )
    async def get_my_profile(
            self,
    ):
        result = await self.manager.get_profile_by_user(self.user)
        return result

    @router.get(
        "/{user_id}",
        summary="getting user's profile",
        response_model=GetProfile
    )
    async def get_profile(
            self,
            get_user: User = Depends(get_user_or_404)
    ):
        result = await self.manager.get_profile(self.user, get_user)
        return result