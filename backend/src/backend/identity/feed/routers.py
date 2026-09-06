from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.schemas import PageRequest, PageResult
from src.backend.identity.feed.dependencies import get_feed_manager
from src.backend.identity.feed.managers import FeedManager
from src.backend.identity.feed.schemas import FeedItem
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

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
    )
    async def get_home_feed(
            self,
            page: int = Query(default=1, ge=1),
            size: int = Query(default=50, ge=1),
    ):
        """Returns the current user's home feed"""
        result = await self.manager.get_home_feed(self.user, PageRequest(page=page, size=size))
        return result
