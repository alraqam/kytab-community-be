from fastapi import APIRouter, Depends, Query, status
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.schemas import PageRequest, PageResult
from src.backend.identity.feed.dependencies.feed import get_feed_manager
from src.backend.identity.feed.managers.feed import FeedManager
from src.backend.identity.feed.schemas.feed import FeedItem
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/feed",
    tags=["feed"]
)

@cbv(router)
class FeedRouter:
    """CBV router for the home feed."""

    manager: FeedManager = Depends(get_feed_manager)
    user: User = Depends(get_current_user)

    @router.get(
        "/home",
        summary="getting home feed",
        response_model=PageResult[FeedItem],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_home_feed(
            self,
            page: int = Query(default=1, ge=1),
            size: int = Query(default=50, ge=1),
    ):
        """Returns the current user's home feed"""
        result = await self.manager.get_home_feed(self.user, PageRequest(page=page, size=size))
        return result
