"""Celery application setup: broker/result backend, task discovery, and the periodic beat schedule."""

from celery import Celery
from celery.schedules import crontab

from src.backend.core.settings import settings

celery_app = Celery(
    broker=settings.RABBITMQ_URL,
    backend="redis://redis:6379/1",
    include=[
        "src.backend.core.all_models",
        "src.backend.tasks",
        "src.backend.identity.auth.services.email",
        "src.backend.clubs.club_membership.email",
        "src.backend.notifications.email",
        "src.backend.notifications.push",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "check-expired-invitations": {
        "task": "src.backend.tasks.invitations.check_expired_invitations",
        "schedule": 60.0,
    },
    "check-join-requests": {
        "task": "src.backend.tasks.requests.check_expired_join_requests",
        "schedule": 60.0,
    },
    "check-user-deletions": {
        "task": "src.backend.tasks.delete_account.delete_user_account",
        "schedule": 60.0,
    },
    "send-deadline-reminders": {
        "task": "src.backend.tasks.event_reminders.send_event_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    "send-daily-digests": {
        "task": "src.backend.tasks.digests.send_daily_digests",
        "schedule": crontab(hour=8, minute=0),
    },
    "send-weekly-digests": {
        "task": "src.backend.tasks.digests.send_weekly_digests",
        "schedule": crontab(day_of_week="mon", hour=8, minute=0),
    },
}

celery_app.conf.timezone = "UTC"