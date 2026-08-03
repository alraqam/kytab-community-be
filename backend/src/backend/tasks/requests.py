from datetime import datetime
from sqlalchemy import update, and_

from src.backend.core.task import task_session
from src.backend.clubs.club_membership.exceptions import ExpiredRequestError
from src.backend.clubs.club_membership.models import ClubJoinRequest
from src.backend.clubs.club_membership.schemas import JoinRequestStatus
from src.backend.celery_app import celery_app


async def _check_expired_join_requests() -> None:
    """Marks expired pending join requests as expired. Triggered every 60 seconds by celery beat.

    Raises:
        ExpiredRequestError: When the update fails for any reason.
    """
    try:
        async with task_session() as session:
            await session.execute(
                update(ClubJoinRequest)
                .where(
                    and_(
                        ClubJoinRequest.expires_at <= datetime.now(),
                        ClubJoinRequest.status == JoinRequestStatus.pending,
                    )
                )
                .values(status=JoinRequestStatus.expired)
            )
            await session.commit()
    except Exception as e:
        raise ExpiredRequestError(f"Error expiring invitations: {e}")

@celery_app.task
def check_expired_join_requests():
    """Celery task that marks expired pending club join requests as expired."""
    import asyncio
    asyncio.run(_check_expired_join_requests())