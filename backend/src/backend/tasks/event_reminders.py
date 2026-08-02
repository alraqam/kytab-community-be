from datetime import timedelta, datetime, timezone

from src.backend.core.task import task_session
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.events.managers.event import ClubEventManager
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType
from src.backend.celery_app import celery_app

async def _send_event_reminders():
    date = (datetime.now(timezone.utc) + timedelta(days=3)).date()

    async with task_session() as session:
        event_manager = ClubEventManager(session)
        membership_manager = ClubMembershipManager(session)
        notification_manager = NotificationManager(session)
        user_manager = UserManager(session)

        events = await event_manager.get_event_with_date(date)
        for event in events:
            members = await membership_manager.get_club_members(event.club)
            recipients = [
                await user_manager.get_user_by_id(member.user_id)
                for member in members
            ]

            await notification_manager.notify_many(
                recipients,
                category=NotificationCategory.event_reminder,
                title=f"{event.club.name} has an event in 3 days. {event.name} starts at {event.start_at}",
                object_type=NotificationObjectType.event,
                object_id=event.id,
                club_id=event.club.id,
            )
        await session.commit()

@celery_app.task
def send_event_reminders():
    import asyncio
    asyncio.run(_send_event_reminders())