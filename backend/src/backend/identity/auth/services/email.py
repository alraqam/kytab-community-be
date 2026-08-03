import asyncio
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from src.backend.celery_app import celery_app
from src.backend.core.services import _send_email_sync
from src.backend.core.settings import settings
from src.backend.identity.auth.exceptions import InvalidTokenTypeError, InvalidTokenError
from src.backend.identity.auth.models import User


def create_verification_token(user_id: int) -> str:
    """Creates a signed JWT for email verification, valid for 24 hours.

    Args:
        user_id: ID of the user to embed as the subject claim.

    Returns:
        Signed JWT string.
    """
    payload = {
        "sub": str(user_id),
        "type": "email_verification",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm="HS256")

def decode_verification_token(token: str) -> int:
    """Decodes and validates an email verification JWT.

    Args:
        token: Signed JWT string to decode.

    Returns:
        ID of the user the token was issued for.

    Raises:
        InvalidTokenTypeError: When the token's type claim is not "email_verification".
    """
    payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=["HS256"])
    if payload.get("type") != "email_verification":
        raise InvalidTokenTypeError("Invalid token type")
    return int(payload["sub"])

def _reset_key(user) -> str:
    """Derives a per-user signing key for password-reset tokens.

    Args:
        user: User whose current password hash is mixed into the key.

    Returns:
        Signing key string combining the app secret and the user's password hash.
    """
    return settings.TOKEN_SECRET_KEY + user.hashed_password

def create_password_reset_token(user: User) -> str:
    """Creates a signed JWT for password reset, valid for 10 minutes.

    The token is signed with a key derived from the user's current password
    hash, so it is invalidated automatically once the password changes.

    Args:
        user: User to issue the reset token for.

    Returns:
        Signed JWT string.
    """
    payload = {
        "sub": str(user.id),
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    return jwt.encode(payload, _reset_key(user), algorithm="HS256")

async def decode_password_reset_token(token: str, manager) -> int:
    """Decodes and validates a password-reset JWT against the target user's reset key.

    Args:
        token: Signed JWT string to decode.
        manager: Manager providing get_user_by_id, used to resolve the token's subject user.

    Returns:
        ID of the user the token was issued for.

    Raises:
        InvalidTokenError: When the token is malformed, expired, references a
            missing user, or is not a password_reset token.
    """
    try:
        unverified = jwt.get_unverified_claims(token)
        user = await manager.get_user_by_id(int(unverified["sub"]))
        if not user:
            raise InvalidTokenError("Invalid token")

        payload = jwt.decode(token, _reset_key(user), algorithms=["HS256"])
    except (JWTError, KeyError, ValueError):
        raise InvalidTokenError("Invalid or expired token")

    if payload.get("type") != "password_reset":
        raise InvalidTokenError("Invalid token")
    return user.id

@celery_app.task
def send_verification_email(to_email: str, token: str) -> None:
    """Celery task that sends an email-verification email synchronously in a background worker.

    Args:
        to_email: Recipient email address.
        token: Email verification token to embed in the link.
    """
    asyncio.run(_send_verification_email_async(to_email, token))

async def _send_verification_email_async(to_email: str, token: str) -> None:
    """Builds and sends the verification email.

    Args:
        to_email: Recipient email address.
        token: Email verification token to embed in the link.
    """
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f'<p>Click <a href="{link}">here</a> to verify your email. Expires in 24h.</p>'
    await asyncio.to_thread(_send_email_sync, to_email, "Verify your email", html)

@celery_app.task
def send_password_reset_email(to_email: str, token: str) -> None:
    """Celery task that sends a password-reset email synchronously in a background worker.

    Args:
        to_email: Recipient email address.
        token: Password-reset token to embed in the link.
    """
    asyncio.run(_send_password_reset_email(to_email, token))

async def _send_password_reset_email(to_email: str, token: str) -> None:
    """Builds and sends the password-reset email.

    Args:
        to_email: Recipient email address.
        token: Password-reset token to embed in the link.
    """
    link = f"{settings.FRONTEND_URL}/password_reset?token={token}"
    html = f'<p>Click <a href="{link}">here</a> to reset your password. Expires in 10 minutes.</p>'
    await asyncio.to_thread(_send_email_sync, to_email, "Password reset", html)