from dataclasses import dataclass

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.notifications.models import PushSubscription


@dataclass
class PushSubscriptionRepository:
    """Data-access layer for push subscription persistence and queries."""

    session: AsyncSession

    async def create_subscription(
            self,
            user_id: int,
            endpoint: str,
            p256dh: str,
            auth: str,
    ) -> PushSubscription:
        """Inserts a new push subscription.

        Args:
            user_id: ID of the user the subscription belongs to.
            endpoint: Push service endpoint URL.
            p256dh: Subscription's p256dh public key.
            auth: Subscription's auth secret.

        Returns:
            Newly created PushSubscription instance.
        """
        result = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_subscription(
            self,
            subscription: PushSubscription,
            p256dh: str,
            auth: str,
    ) -> None:
        """Updates an existing subscription's encryption keys.

        Args:
            subscription: PushSubscription instance to update.
            p256dh: New p256dh public key.
            auth: New auth secret.
        """
        subscription.p256dh = p256dh
        subscription.auth = auth
        await self.session.flush()

    async def delete_by_endpoint(
            self,
            endpoint: str,
    ) -> None:
        """Deletes a push subscription by its endpoint, if one exists.

        Args:
            endpoint: Push service endpoint URL to remove.
        """
        await self.session.execute(delete(PushSubscription).where(PushSubscription.endpoint == endpoint))
        await self.session.flush()

    async def delete_for_user(
            self,
            user_id: int,
            endpoint: str,
    ) -> None:
        """Deletes a user's push subscription by endpoint.

        Args:
            user_id: ID of the user the subscription must belong to.
            endpoint: Push service endpoint URL to remove.
        """
        await self.session.execute(
            delete(PushSubscription).where(
                and_(
                    PushSubscription.user_id == user_id,
                    PushSubscription.endpoint == endpoint,
                )
            )
        )
        await self.session.flush()

    async def get_by_endpoint(
            self,
            endpoint: str,
    ) -> PushSubscription | None:
        """Fetches a subscription by its endpoint.

        Args:
            endpoint: Push service endpoint URL to look up.

        Returns:
            Matching PushSubscription instance, or None if not found.
        """
        stmt = select(PushSubscription).where(PushSubscription.endpoint == endpoint)
        result = await self.session.execute(stmt)
        subscription = result.scalar_one_or_none()
        return subscription

    async def get_by_user(
            self,
            user_id: int,
    ) -> list[PushSubscription]:
        """Lists all push subscriptions for a user.

        Args:
            user_id: ID of the user whose subscriptions to list.

        Returns:
            List of matching PushSubscription instances.
        """
        stmt = select(PushSubscription).where(PushSubscription.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst
