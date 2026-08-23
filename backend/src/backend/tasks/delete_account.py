from datetime import datetime, timezone, timedelta

from sqlalchemy import delete, and_

from src.backend.celery_app import celery_app
from src.backend.core.task import task_session
from src.backend.identity.auth.models import User
from src.backend.identity.users.exceptions import UserDeletionError

async def _delete_user_account():
    try:
        async with task_session() as session:
            await session.execute(
                delete(User)
                .where(
                    and_(
                        User.is_deleted == True,
                        User.deleted_at + timedelta(days=30) <= datetime.now(timezone.utc)
                    )
                )
            )
            await session.commit()
    except Exception as e:
        raise UserDeletionError(f"Error user deletion: {e}")

@celery_app.task
def delete_user_account():
    """Celery task that deletes user accounts after 30 days of soft deletion."""
    import asyncio
    asyncio.run(_delete_user_account())