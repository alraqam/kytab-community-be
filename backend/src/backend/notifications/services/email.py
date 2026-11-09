import asyncio

from src.backend.celery_app import celery_app
from src.backend.core.services import _send_email_sync

@celery_app.task
def send_notification_email(to_email: str, title: str, body: str | None) -> None:
    """Celery task that sends a notification as an email.

    Args:
        to_email: Recipient email address.
        title: Notification title, used as the email subject.
        body: Notification body, or None to fall back to the title as the email content.
    """
    asyncio.run(_send_notification_email(to_email, title, body))

async def _send_notification_email(to_email: str, title: str, body: str | None) -> None:
    """Builds the HTML email body for a notification and sends it.

    Args:
        to_email: Recipient email address.
        title: Notification title, used as the email subject and fallback content.
        body: Notification body, or None to fall back to the title.
    """
    html = f"<p>{body or title}</p>"
    await asyncio.to_thread(_send_email_sync, to_email, title, html)

@celery_app.task
def send_digest_email(to_email: str, titles: list[str]) -> None:
    """Celery task that sends a digest email summarizing recent notification titles.

    Args:
        to_email: Recipient email address.
        titles: Titles of the notifications to include in the digest.
    """
    asyncio.run(_send_digest_email(to_email, titles))

async def _send_digest_email(to_email: str, titles: list[str]) -> None:
    """Builds the HTML body for a digest email and sends it.

    Args:
        to_email: Recipient email address.
        titles: Titles of the notifications to include in the digest.
    """
    items = "".join(f"<li>{title}</li>" for title in titles)
    html = f"<p>You have {len(titles)} new updates:</p><ul>{items}</ul>"
    await asyncio.to_thread(_send_email_sync, to_email, "Your activity digest", html)
