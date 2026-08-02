import asyncio

from src.backend.celery_app import celery_app
from src.backend.core.services import _send_email_sync

@celery_app.task
def send_notification_email(to_email: str, title: str, body: str | None) -> None:
    asyncio.run(_send_notification_email(to_email, title, body))

async def _send_notification_email(to_email: str, title: str, body: str | None) -> None:
    html = f"<p>{body or title}</p>"
    await asyncio.to_thread(_send_email_sync, to_email, title, html)
