from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi_utils.cbv import cbv

from src.backend.core.dependencies import get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.identity.profile.dependencies.profile import get_profile_manager
from src.backend.identity.profile.managers.profile import ProfileManager
from src.backend.identity.profile.schemas.profile import UpdateProfile, UpdateProfileVisibility, GetProfile, to_get_profile
from src.backend.identity.users.dependencies.user import get_user_or_404
from src.backend.core.responses import error_responses

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
        summary="updating avatar",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 404),
    )
    async def update_avatar(
            self,
            avatar: UploadFile = File(...),
    ):
        """Uploads a new avatar image for the current user."""
        await self.manager.update_avatar(self.user, avatar)

    @router.put(
        "/{user_id}/profile",
        summary="updating profile",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(400, 401, 404),
    )
    async def update_profile(
            self,
            request: UpdateProfile,
    ):
        """Updates the current user's profile fields."""
        await self.manager.update_profile(self.user, request)

    @router.put(
        "/{user_id}/visibility",
        summary="updating visibility",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 404),
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
        response_model=GetProfile,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
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
        response_model=GetProfile,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_profile(
            self,
            get_user: User = Depends(get_user_or_404)
    ):
        """Fetches another user's profile, enforcing visibility rules."""
        result = await self.manager.get_profile(self.user, get_user)
        return to_get_profile(result, self.storage.presigned_url(result.avatar))