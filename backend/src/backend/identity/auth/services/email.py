import asyncio
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from src.backend.core.services import _send_email_sync
from src.backend.core.settings import settings
from src.backend.identity.auth.exceptions import InvalidTokenTypeError, InvalidTokenError
from src.backend.identity.auth.models import User


def create_verification_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "email_verification",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm="HS256")

def decode_verification_token(token: str) -> int:
    payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=["HS256"])
    if payload.get("type") != "email_verification":
        raise InvalidTokenTypeError("Invalid token type")
    return int(payload["sub"])

def _reset_key(user) -> str:
    return settings.TOKEN_SECRET_KEY + user.hashed_password

def create_password_reset_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    return jwt.encode(payload, _reset_key(user), algorithm="HS256")

async def decode_password_reset_token(token: str, manager) -> int:
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

async def send_verification_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f'<p>Click <a href="{link}">here</a> to verify your email. Expires in 24h.</p>'
    await asyncio.to_thread(_send_email_sync, to_email, "Verify your email", html)

async def send_password_reset_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/password_reset?token={token}"
    html = f'<p>Click <a href="{link}">here</a> to reset your password. Expires in 10 minutes.</p>'
    await asyncio.to_thread(_send_email_sync, to_email, "Password reset", html)