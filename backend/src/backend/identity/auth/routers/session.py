from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_session_manager, get_current_user, get_session_or_404
from src.backend.identity.auth.managers.session import SessionManager
from src.backend.identity.auth.models import User, Session
from src.backend.identity.auth.schemas import GetSession
from src.backend.identity.users.dependencies import get_user_manager
from src.backend.identity.users.managers import UserManager

router = APIRouter(
    prefix="/session",
    tags=["sessions"]
)

@cbv(router)
class SessionRouter:
    manager: SessionManager = Depends(get_session_manager)
    user_manager: UserManager = Depends(get_user_manager)

    @router.get(
        "/",
        summary="getting user's active sessions",
        response_model=list[GetSession]
    )
    async def get_user_sessions(
            self,
            user: User = Depends(get_current_user)
    ):

        response = await self.manager.get_user_sessions(user)
        return response

    @router.delete(
        "/{session_id}",
        summary="revoking session",
    )
    async def revoke(
            self,
            user: User = Depends(get_current_user),
            session: Session = Depends(get_session_or_404)
    ):

        response = await self.manager.revoke(user, session)
        return response
