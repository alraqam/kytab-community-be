from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models import Thread
from src.backend.core.dependencies import get_db


async def get_thread_manager(
        session: AsyncSession = Depends(get_db)
) -> ThreadManager:
    return ThreadManager(session)

async def get_thread_or_404(
        thread_id: int,
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    result = await manager.get_thread_by_id(thread_id)
    return result
