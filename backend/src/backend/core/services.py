import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

from src.backend.core.settings import settings


def is_valid_url(url: str) -> bool:
    """Checks whether a string is a valid HTTP or HTTPS URL.

    Args:
        url: URL string to validate.

    Returns:
        True if the URL has a valid scheme (http/https) and netloc; False otherwise.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False

def _send_email_sync(to_email: str, subject: str, html_body: str) -> None:
    """Sends an HTML email synchronously over SMTP using the configured server credentials.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        html_body: HTML body content of the email.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)