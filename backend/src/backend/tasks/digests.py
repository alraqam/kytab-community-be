from datetime import datetime, timedelta

from src.backend.core.task import task_session
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.email import send_digest_email
from src.backend.notifications.repository.notification import NotificationRepository
from src.backend.notifications.repository.preference import NotificationPreferenceRepository
from src.backend.notifications.schemas import DigestFrequency
from src.backend.celery_app import celery_app

_DIGEST_WINDOWS = {
    DigestFrequency.daily: timedelta(days=1),
    DigestFrequency.weekly: timedelta(days=7),
}

async def _send_digests(frequency: DigestFrequency) -> None:
    """Sends a digest email to every user opted into the given digest frequency.

    Args:
        frequency: Digest frequency to process ("daily" or "weekly").
    """
    now = datetime.now()

    async with task_session() as session:
        preference_repo = NotificationPreferenceRepository(session)
        notification_repo = NotificationRepository(session)
        user_manager = UserManager(session)

        preferences = await preference_repo.get_by_digest_frequency(frequency)
        for preference in preferences:
            since = preference.last_digest_sent_at or (now - _DIGEST_WINDOWS[frequency])
            notifications = await notification_repo.get_notifications_since(
                preference.user_id, preference.category, preference.club_id, since
            )
            if notifications:
                user = await user_manager.get_user_by_id(preference.user_id)
                send_digest_email.delay(user.email, [notification.title for notification in notifications])
            await preference_repo.update_last_digest_sent_at(preference, now)
        await session.commit()

@celery_app.task
def send_daily_digests():
    """Celery task that sends digest emails for all preferences set to a daily digest."""
    import asyncio
    asyncio.run(_send_digests(DigestFrequency.daily))

@celery_app.task
def send_weekly_digests():
    """Celery task that sends digest emails for all preferences set to a weekly digest."""
    import asyncio
    asyncio.run(_send_digests(DigestFrequency.weekly))
