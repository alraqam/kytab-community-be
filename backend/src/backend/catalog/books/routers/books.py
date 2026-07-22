from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import WorkFilter
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.work import GetWork
from src.backend.catalog.books.services import DEFAULT_LANGUAGE, fetch_from_open_library, cache_work
from src.backend.core.dependencies import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"]
)


@cbv(router)
class BooksRouter:
    """CBV router exposing the public book catalog under /books."""

    session: AsyncSession = Depends(get_db)

    @router.get(
        "/",
        summary="getting all books or searching by title/description",
        response_model=list[GetWork],
    )
    async def get_books(
            self,
            q: str | None = Query(default=None),
            language: str = Query(default=DEFAULT_LANGUAGE),
    ):
        """Returns cached books, searching Open Library when the local catalog has no match.

        Args:
            q: Optional search string. When set and the local catalog has no
                matching works, Open Library is queried and the results are
                cached before being returned.
            language: ISO 639-2 language code used for the Open Library search
                and for the cached work's primary language.

        Returns:
            List of Work instances matching the query (or all works when no query is given).
        """
        work_repo = WorkRepository(self.session)
        filters = WorkFilter(q=q) if q else None
        works = await work_repo.get_all_works(filters)

        if works or not q:
            return works

        ol_items = await fetch_from_open_library(q, language)
        for item in ol_items:
            await cache_work(item, self.session, language)

        return await work_repo.get_all_works(filters)
