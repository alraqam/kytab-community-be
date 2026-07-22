from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.backend.core.settings import settings

engine = create_async_engine(settings.ASYNC_DATABASE_URL , echo=True)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)