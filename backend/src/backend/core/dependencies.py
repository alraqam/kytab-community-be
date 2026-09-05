from src.backend.core.session import async_session
from src.backend.core.storage import StorageService


async def get_db():
    """FastAPI dependency that provides an async SQLAlchemy session.

    Yields:
        AsyncSession: Active database session; automatically closed after the request.
    """
    async with async_session() as session:
        yield session

async def get_storage_service() -> StorageService:
    """FastAPI dependency that provides a StorageService instance.

    Returns:
        StorageService bound to the configured S3-compatible bucket.
    """
    return StorageService()