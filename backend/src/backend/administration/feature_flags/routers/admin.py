from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.administration.feature_flags.dependencies import get_feature_flag_manager, get_feature_flag_or_404
from src.backend.administration.feature_flags.filters import FeatureFlagFilter
from src.backend.administration.feature_flags.managers import FeatureFlagManager
from src.backend.administration.feature_flags.models import FeatureFlag
from src.backend.administration.feature_flags.schemas import CreateFeatureFlag, UpdateFeatureFlag, GetFeatureFlag
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.audit_log.decorators import audit_action
from src.backend.trust_safety.audit_log.schemas import AuditLogAction

router = APIRouter(
    prefix="/admin/feature-flags",
    tags=["admin"]
)

@cbv(router)
class FeatureFlagAdminRouter:
    """CBV router for admin management of feature flags: create, update, enable/disable, and delete."""

    manager: FeatureFlagManager = Depends(get_feature_flag_manager)
    user: User = Depends(is_admin)

    @router.post(
        "/",
        summary="creating feature flag",
        response_model=GetFeatureFlag
    )
    @audit_action(AuditLogAction.feature_flag_created, "feature_flag", id_from="result")
    async def create_feature_flag(
            self,
            request: CreateFeatureFlag
    ):
        """Creates a new feature flag."""
        result = await self.manager.create_feature_flag(self.user, request)
        return result

    @router.put(
        "/{flag_id}",
        summary="updating feature flag",
    )
    @audit_action(AuditLogAction.feature_flag_updated, "feature_flag", id_from="flag")
    async def update_feature_flag(
            self,
            request: UpdateFeatureFlag,
            flag: FeatureFlag = Depends(get_feature_flag_or_404),
    ):
        """Updates a feature flag's name, description, and/or rollout percentage."""
        await self.manager.update_feature_flag(flag, request)

    @router.put(
        "/{flag_id}/enable",
        summary="enabling feature flag",
    )
    @audit_action(AuditLogAction.feature_flag_enabled, "feature_flag", id_from="flag")
    async def enable_feature_flag(
            self,
            flag: FeatureFlag = Depends(get_feature_flag_or_404),
    ):
        """Enables a feature flag for rollout."""
        await self.manager.enable_feature_flag(flag)

    @router.put(
        "/{flag_id}/disable",
        summary="disabling feature flag",
    )
    @audit_action(AuditLogAction.feature_flag_disabled, "feature_flag", id_from="flag")
    async def disable_feature_flag(
            self,
            flag: FeatureFlag = Depends(get_feature_flag_or_404),
    ):
        """Disables a feature flag."""
        await self.manager.disable_feature_flag(flag)

    @router.delete(
        "/{flag_id}",
        summary="deleting feature flag",
    )
    @audit_action(AuditLogAction.feature_flag_deleted, "feature_flag", id_from="flag")
    async def delete_feature_flag(
            self,
            flag: FeatureFlag = Depends(get_feature_flag_or_404),
    ):
        """Deletes a feature flag."""
        await self.manager.delete_feature_flag(flag)

    @router.get(
        "/",
        summary="getting feature flags",
        response_model=list[GetFeatureFlag]
    )
    async def get_feature_flags(
            self,
            filters: FeatureFlagFilter = FilterDepends(FeatureFlagFilter)
    ):
        """Lists feature flags, optionally filtered and sorted."""
        result = await self.manager.get_feature_flags(filters)
        return result

    @router.get(
        "/{flag_id}",
        summary="getting feature flag by id",
        response_model=GetFeatureFlag
    )
    async def get_feature_flag_by_id(
            self,
            flag: FeatureFlag = Depends(get_feature_flag_or_404),
    ):
        """Fetches a single feature flag by ID."""
        return flag
