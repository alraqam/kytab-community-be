import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

from fastapi import UploadFile

from src.backend.core.settings import settings

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


async def validate_image_upload(file: UploadFile, error_cls: type[Exception]) -> tuple[bytes, str]:
    """Validates an uploaded image's content type and size.

    Args:
        file: Uploaded file to validate.
        error_cls: Exception class to raise when validation fails.

    Returns:
        Tuple of the file's raw bytes and the extension to store it under.

    Raises:
        error_cls: When the content type is unsupported or the file exceeds the size limit.
    """
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise error_cls("Unsupported image type")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise error_cls("Image exceeds maximum allowed size")

    return content, ALLOWED_IMAGE_CONTENT_TYPES[file.content_type]


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