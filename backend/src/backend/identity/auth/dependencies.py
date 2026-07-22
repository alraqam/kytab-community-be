from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.core.dependencies import get_db
from src.backend.identity.auth.managers.auth import AuthManager
from src.backend.identity.auth.managers.session import SessionManager
from src.backend.identity.auth.models import User, Session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency that resolves and returns the authenticated user from the Bearer token.

    Args:
        token: JWT access token extracted by OAuth2PasswordBearer.
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        Authenticated User instance.

    Raises:
        InvalidTokenError: When the token is invalid or the user is not found.
    """
    manager = AuthManager(session)
    user = await manager.get_me(token)
    return user


async def get_auth_manager(
        session: AsyncSession = Depends(get_db)
):
    """FastAPI dependency that provides an AuthManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        AuthManager bound to the current session.
    """
    return AuthManager(session)


async def get_session_manager(
        session: AsyncSession = Depends(get_db)
) -> SessionManager:
    return SessionManager(session)


async def get_session_or_404(
        session_id: int,
        manager: SessionManager = Depends(get_session_manager)
) -> Session:
    return await manager.get_session_by_id(session_id)