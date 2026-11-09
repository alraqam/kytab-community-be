from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.notifications.dependencies.notification import get_push_subscription_manager
from src.backend.notifications.managers.push_subscription import PushSubscriptionManager
from src.backend.notifications.schemas.notification import CreatePushSubscription, DeletePushSubscription, GetPushSubscription
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/notifications/push-subscriptions",
    tags=["push_subscriptions"]
)

@cbv(router)
class PushSubscriptionRouter:
    """CBV router for registering and removing the current user's Web Push subscriptions."""

    manager: PushSubscriptionManager = Depends(get_push_subscription_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="registering a push subscription",
        response_model=GetPushSubscription,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401),
    )
    async def subscribe(
            self,
            request: CreatePushSubscription
    ):
        """Registers the current user's browser push subscription."""
        result = await self.manager.subscribe(self.user, request)
        return result

    @router.delete(
        "/",
        summary="removing a push subscription",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401),
    )
    async def unsubscribe(
            self,
            request: DeletePushSubscription
    ):
        """Removes one of the current user's push subscriptions."""
        await self.manager.unsubscribe(self.user, request.endpoint)
