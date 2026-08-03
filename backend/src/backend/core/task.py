from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.backend.core.settings import settings


@asynccontextmanager
async def task_session():
    """Provides a standalone async SQLAlchemy session for use outside request context (e.g. Celery tasks).

    Yields:
        AsyncSession: Database session backed by a dedicated engine, disposed on exit.
    """
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()