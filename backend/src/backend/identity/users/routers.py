from fastapi import APIRouter, Depends

from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import get_user_manager, is_admin, get_user_or_404
from src.backend.identity.users.filters import UserFilter
from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.schemas import UpdateUserRole, UpdateUserActivity, GetAdminUser

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"]
)

@cbv(router)
class UserRouter:
    """CBV router exposing admin-only user management endpoints under /users."""

    manager: UserManager = Depends(get_user_manager)
    user: User = Depends(is_admin)

    @router.put(
        "/{user_id}/role",
        summary="updating user role"
    )
    async def update_user_role(
            self,
            request: UpdateUserRole,
            user: User = Depends(get_user_or_404)
    ):
        """Updates the role of the specified user."""
        await self.manager.update_user_role(user, request)

    @router.put(
        "/{user_id}/activity",
        summary="updating user activity"
    )
    async def update_user_activity(
            self,
            request: UpdateUserActivity,
            user: User = Depends(get_user_or_404)
    ):
        """Updates the active status of the specified user."""
        await self.manager.update_user_activity(user, request)

    @router.delete(
        "/{user_id}",
        summary="deleting user"
    )
    async def delete_user(
            self,
            user: User = Depends(get_user_or_404)
    ):
        """Permanently deletes the specified user."""
        await self.manager.delete_user(user)

    @router.get(
        "/{user_id}",
        summary="getting user by id",
        response_model=GetAdminUser,
    )
    async def get_user(
            self,
            user: User = Depends(get_user_or_404)
    ):
        """Returns the specified user."""
        return user

    @router.get(
        "/",
        summary="getting all users",
        response_model=list[GetAdminUser],
    )
    async def get_users(
            self,
            filters: UserFilter = FilterDepends(UserFilter)
    ):
        """Returns all users matching the given filter parameters."""
        users = await self.manager.get_all_users(filters)
        return users