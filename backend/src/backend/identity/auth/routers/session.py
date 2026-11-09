from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_session_manager, get_current_user, get_session_or_404
from src.backend.identity.auth.managers.session import SessionManager
from src.backend.identity.auth.models.auth import User, Session
from src.backend.identity.auth.schemas.auth import GetSession
from src.backend.identity.users.dependencies.user import get_user_manager
from src.backend.identity.users.managers.user import UserManager
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/session",
    tags=["sessions"]
)

@cbv(router)
class SessionRouter:
    """CBV router for session management endpoints: listing and revoking sessions."""

    manager: SessionManager = Depends(get_session_manager)
    user_manager: UserManager = Depends(get_user_manager)

    @router.get(
        "/",
        summary="getting user's active sessions",
        response_model=list[GetSession],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_sessions(
            self,
            user: User = Depends(get_current_user)
    ):
        """Lists the currently authenticated user's active sessions."""
        response = await self.manager.get_user_sessions(user)
        return response

    @router.delete(
        "/{session_id}",
        summary="revoking session",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def revoke(
            self,
            user: User = Depends(get_current_user),
            session: Session = Depends(get_session_or_404)
    ):
        """Revokes the given session if it belongs to the authenticated user."""
        response = await self.manager.revoke(user, session)
        return response
