from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.administration.feature_flags.dependencies import get_feature_flag_manager
from src.backend.administration.feature_flags.managers import FeatureFlagManager
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/feature-flags",
    tags=["feature_flags"]
)

@cbv(router)
class FeatureFlagPublicRouter:
    """CBV router letting the current user evaluate which enabled feature flags apply to them."""

    manager: FeatureFlagManager = Depends(get_feature_flag_manager)
    user: User = Depends(get_current_user)

    @router.get(
        "/",
        summary="evaluating feature flags for current user",
        response_model=dict[str, bool]
    )
    async def evaluate_feature_flags(self):
        """Evaluates every enabled feature flag's staged rollout for the current user."""
        result = await self.manager.evaluate_flags_for_user(self.user)
        return result
