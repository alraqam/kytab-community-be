from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.notifications.models import PushSubscription
from src.backend.notifications.repository.push_subscription import PushSubscriptionRepository
from src.backend.notifications.schemas import CreatePushSubscription


class PushSubscriptionManager:
    """Handles push subscription business logic: registering and removing a device's Web Push endpoint."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.push_subscription_repo = PushSubscriptionRepository(session)

    async def subscribe(
            self,
            user: User,
            request: CreatePushSubscription,
    ) -> PushSubscription:
        """Registers a push subscription for the user, updating it in place if the endpoint is already known.

        Args:
            user: User the subscription belongs to.
            request: CreatePushSubscription payload with the endpoint and encryption keys.

        Returns:
            Created or updated PushSubscription instance.
        """
        existing = await self.push_subscription_repo.get_by_endpoint(request.endpoint)
        if existing:
            await self.push_subscription_repo.update_subscription(existing, request.p256dh, request.auth)
            result = existing
        else:
            result = await self.push_subscription_repo.create_subscription(
                user_id=user.id,
                endpoint=request.endpoint,
                p256dh=request.p256dh,
                auth=request.auth,
            )
        await self.session.commit()
        return result

    async def unsubscribe(
            self,
            user: User,
            endpoint: str,
    ) -> None:
        """Removes one of the user's push subscriptions by endpoint.

        Args:
            user: User the subscription belongs to.
            endpoint: Push service endpoint URL to remove.
        """
        await self.push_subscription_repo.delete_for_user(user.id, endpoint)
        await self.session.commit()
