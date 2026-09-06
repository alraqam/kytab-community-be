import asyncio
import json

from pywebpush import webpush, WebPushException

from src.backend.celery_app import celery_app
from src.backend.core.settings import settings

@celery_app.task
def send_notification_push(endpoint: str, p256dh: str, auth: str, title: str, body: str | None) -> None:
    """Celery task that delivers a notification to a single Web Push subscription.

    Args:
        endpoint: Push service endpoint URL for the subscription.
        p256dh: Subscription's p256dh public key, used to encrypt the payload.
        auth: Subscription's auth secret, used to encrypt the payload.
        title: Notification title, used as the push message title.
        body: Optional notification body.
    """
    try:
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth},
            },
            data=json.dumps({"title": title, "body": body or ""}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}"},
        )
    except WebPushException as exc:
        if exc.response is not None and exc.response.status_code in (404, 410):
            asyncio.run(_remove_stale_subscription(endpoint))

async def _remove_stale_subscription(endpoint: str) -> None:
    """Deletes a push subscription that the push service reports as no longer valid.

    Args:
        endpoint: Push service endpoint URL to remove.
    """
    from src.backend.core.task import task_session
    from src.backend.notifications.repository.push_subscription import PushSubscriptionRepository

    async with task_session() as session:
        await PushSubscriptionRepository(session).delete_by_endpoint(endpoint)
        await session.commit()
