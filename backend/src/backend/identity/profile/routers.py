from fastapi import APIRouter, Depends, File, UploadFile
from fastapi_utils.cbv import cbv

from src.backend.core.dependencies import get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.profile.dependencies import get_profile_manager
from src.backend.identity.profile.managers import ProfileManager
from src.backend.identity.profile.schemas import UpdateProfile, UpdateProfileVisibility, GetProfile, to_get_profile
from src.backend.identity.users.dependencies import get_user_or_404

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@cbv(router)
class ProfileRouter:
    """CBV router for authenticated user profile endpoints."""

    manager: ProfileManager = Depends(get_profile_manager)
    storage: StorageService = Depends(get_storage_service)
    user: User = Depends(get_current_user)

    @router.put(
        "/{user_id}/avatar",
        summary="updating avatar"
    )
    async def update_avatar(
            self,
            avatar: UploadFile = File(...),
    ):
        """Uploads a new avatar image for the current user."""
        await self.manager.update_avatar(self.user, avatar)

    @router.put(
        "/{user_id}/profile",
        summary="updating profile"
    )
    async def update_profile(
            self,
            request: UpdateProfile,
    ):
        """Updates the current user's profile fields."""
        await self.manager.update_profile(self.user, request)

    @router.put(
        "/{user_id}/visibility",
        summary="updating visibility"
    )
    async def update_visibility(
            self,
            request: UpdateProfileVisibility,
    ):
        """Updates the current user's profile visibility setting."""
        await self.manager.update_visibility(self.user, request)

    @router.get(
        "/my-profile",
        summary="getting current user's profile",
        response_model=GetProfile
    )
    async def get_my_profile(
            self,
    ):
        """Fetches the current user's own profile."""
        result = await self.manager.get_profile_by_user(self.user)
        return to_get_profile(result, self.storage.presigned_url(result.avatar))

    @router.get(
        "/{user_id}",
        summary="getting user's profile",
        response_model=GetProfile
    )
    async def get_profile(
            self,
            get_user: User = Depends(get_user_or_404)
    ):
        """Fetches another user's profile, enforcing visibility rules."""
        result = await self.manager.get_profile(self.user, get_user)
        return to_get_profile(result, self.storage.presigned_url(result.avatar))