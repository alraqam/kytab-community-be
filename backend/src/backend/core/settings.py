from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
print(BASE_DIR)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and the project .env file."""

    ACCESS_EXPIRES: int
    REFRESH_EXPIRES: int
    TOKEN_ALGORITHM: str
    TOKEN_SECRET_KEY: str

    ASYNC_DATABASE_URL: str

    DATABASE_URL: str

    BACKEND_URL: str

    GOOGLE_BOOKS_API_KEY: str

    RABBITMQ_URL: str

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    FRONTEND_URL: str

    CLUB_INVITE_SECRET_KEY:str

    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env"
    )

settings = Settings()
