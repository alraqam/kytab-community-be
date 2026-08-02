import asyncio

from src.backend.core.services import _send_email_sync


async def send_notification_email(to_email: str, title: str, body: str | None) -> None:
    html = f"<p>{body or title}</p>"
    await asyncio.to_thread(_send_email_sync, to_email, title, html)
