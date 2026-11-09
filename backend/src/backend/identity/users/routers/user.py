from fastapi import APIRouter, Depends, status

from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import (
    get_user_manager,
    is_admin,
    is_staff,
    get_user_or_404,
    ensure_can_moderate_user,
)
from src.backend.identity.users.filters.user import UserFilter
from src.backend.identity.users.managers.user import UserManager
from src.backend.identity.users.schemas.user import UpdateUserRole, UpdateUserActivity, GetAdminUser
from src.backend.trust_safety.audit_log.decorators.audit import audit_action
from src.backend.trust_safety.audit_log.schemas.audit_log import AuditLogAction
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"]
)

@cbv(router)
class UserRouter:
    """CBV router exposing staff user management endpoints under /admin/users.

    Lookup and suspension are open to platform staff (admins and platform moderators).
    Role changes (including appointing platform moderators) and deletion are admin-only.
    """

    manager: UserManager = Depends(get_user_manager)
    user: User = Depends(is_staff)

    @router.put(
        "/{user_id}/role",
        summary="updating user role",
        dependencies=[Depends(is_admin)],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    @audit_action(AuditLogAction.user_role_updated, "user", id_from="user")
    async def update_user_role(
            self,
            request: UpdateUserRole,
            user: User = Depends(get_user_or_404)
    ):
        """Updates the role of the specified user. Admin-only: this is the only way to create a platform moderator."""
        await self.manager.update_user_role(user, request)

    @router.put(
        "/{user_id}/activity",
        summary="updating user activity",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    @audit_action(AuditLogAction.user_activity_updated, "user", id_from="user")
    async def update_user_activity(
            self,
            request: UpdateUserActivity,
            user: User = Depends(get_user_or_404)
    ):
        """Updates the active status of the specified user. Platform moderators cannot change staff accounts."""
        ensure_can_moderate_user(self.user, user)
        await self.manager.update_user_activity(user, request)

    @router.delete(
        "/{user_id}",
        summary="deleting user",
        dependencies=[Depends(is_admin)],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    @audit_action(AuditLogAction.user_deleted, "user", id_from="user")
    async def delete_user(
            self,
            user: User = Depends(get_user_or_404)
    ):
        """Permanently deletes the specified user. Admin-only."""
        await self.manager.delete_user(user)

    @router.get(
        "/{user_id}",
        summary="getting user by id",
        response_model=GetAdminUser,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
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
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_users(
            self,
            filters: UserFilter = FilterDepends(UserFilter)
    ):
        """Returns all users matching the given filter parameters."""
        users = await self.manager.get_all_users(filters)
        return users
