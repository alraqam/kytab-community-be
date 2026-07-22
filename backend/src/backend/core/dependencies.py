from src.backend.core.session import async_session


async def get_db():
    """FastAPI dependency that provides an async SQLAlchemy session.

    Yields:
        AsyncSession: Active database session; automatically closed after the request.
    """
    async with async_session() as session:
        yield session