"""Celery application setup: broker/result backend, task discovery, and the periodic beat schedule."""

from celery import Celery
from celery.schedules import crontab

from src.backend.core.settings import settings

celery_app = Celery(
    broker=settings.RABBITMQ_URL,
    backend="redis://redis:6379/1",
    include=[
        "src.backend.tasks",
        "src.backend.identity.auth.services.email",
        "src.backend.clubs.club_membership.email",
        "src.backend.notifications.email",
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
    "send-deadline-reminders": {
        "task": "src.backend.tasks.event_reminders.send_event_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
}

celery_app.conf.timezone = "UTC"