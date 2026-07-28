import asyncio
from datetime import timedelta, timezone, datetime

from jose import jwt, JWTError

from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.core.services import _send_email_sync
from src.backend.core.settings import settings
from src.backend.identity.auth.exceptions import InvalidTokenError


def create_club_invite_token(invitation: ClubInvitation) -> str:
    payload = {
        "inv": str(invitation.id),
        "club_id": str(invitation.club_id),
        "type": "club_invite",
        "exp": datetime.now(timezone.utc) + timedelta(days=14),
    }
    return jwt.encode(payload, settings.CLUB_INVITE_SECRET_KEY, algorithm="HS256")

async def decode_club_invite_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.CLUB_INVITE_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise InvalidTokenError("Invalid or expired token")

    if payload.get("type") != "club_invite":
        raise InvalidTokenError("Invalid token")

    try:
        return int(payload["inv"])
    except (KeyError, ValueError):
        raise InvalidTokenError("Invalid token")

async def send_club_invite_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/club_invite?token={token}"
    html = f'<p>Click <a href="{link}">here</a> for more information. Expires in 14 days.</p>'
    await asyncio.to_thread(_send_email_sync, to_email, "Club invitation", html)