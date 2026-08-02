from datetime import datetime
from sqlalchemy import update, and_

from src.backend.core.task import task_session
from src.backend.clubs.club_membership.exceptions import ExpiredInvitationError
from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.clubs.club_membership.schemas import InvitationStatus
from src.backend.celery_app import celery_app


async def _check_expired_invitations() -> None:
    """Marks expired pending invitations as expired. Triggered every 60 seconds by celery beat."""
    try:
        async with task_session() as session:
            await session.execute(
                update(ClubInvitation)
                .where(
                    and_(
                        ClubInvitation.expires_at <= datetime.now(),
                        ClubInvitation.status == InvitationStatus.pending,
                    )
                )
                .values(status=InvitationStatus.expired)
            )
            await session.commit()
    except Exception as e:
        raise ExpiredInvitationError(f"Error expiring invitations: {e}")

@celery_app.task
def check_expired_invitations():
    import asyncio
    asyncio.run(_check_expired_invitations())