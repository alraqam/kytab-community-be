import re

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.models import Work
from src.backend.catalog.books.repository.author import AuthorRepository
from src.backend.catalog.books.repository.edition import EditionRepository
from src.backend.catalog.books.repository.genre import GenreRepository
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.core.exceptions import ServiceUnavailable
from src.backend.core.settings import settings

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes/"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json?"
DEFAULT_LANGUAGE = "eng"


async def fetch_from_open_library(query: str, language: str = DEFAULT_LANGUAGE) -> list[dict]:
    """Searches Open Library for books matching the query.

    Args:
        query: Search string (title, author, or keyword).
        language: ISO 639-2 language code to restrict results to (e.g. "eng", "rus", "uzb").

    Returns:
        List of raw book document dicts from the Open Library API (up to 10).

    Raises:
        ServiceUnavailable: When Open Library cannot be reached or times out.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OPEN_LIBRARY_URL,
                params={
                    "q": query,
                    "lang": language,
                    "limit": 3,
                    "fields": "key,title,author_name,description,first_publish_year,number_of_pages_median,id_google,isbn,cover_i",
                },
                headers={"User-Agent": "BookClub/1.0 (malikarakh07@gmail.com)"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise ServiceUnavailable("Open Library is not reachable right now, please try again later.") from exc

    return data.get("docs", [])


async def fetch_from_google(ol_item: dict, client: httpx.AsyncClient) -> dict | None:
    """Fetches additional book data from Google Books using a Google ID or ISBN.

    Args:
        ol_item: Open Library book document with optional id_google and isbn fields.
        client: Shared async HTTP client.

    Returns:
        Google Books API response dict for the first match, or None if not found
        or if Google Books cannot be reached (enrichment is best-effort and must
        not block caching the Open Library result).
    """
    try:
        google_ids = ol_item.get("id_google", [])
        if google_ids:
            resp = await client.get(
                f"{GOOGLE_BOOKS_URL}{google_ids[0]}",
                params={"key": settings.GOOGLE_BOOKS_API_KEY},
                timeout=10.0,
            )
            if resp.status_code == 200:
                return resp.json()

        isbn = ol_item.get("isbn", [None])[0]
        if isbn:
            resp = await client.get(
                GOOGLE_BOOKS_URL,
                params={"q": f"isbn:{isbn}", "key": settings.GOOGLE_BOOKS_API_KEY},
                timeout=10.0,
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    return items[0]
    except httpx.HTTPError:
        return None

    return None


def _slugify(name: str) -> str:
    """Converts a genre/category name into a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


async def _link_authors(ol_item: dict, work_id: int, author_repo: AuthorRepository) -> None:
    """Gets-or-creates each Open Library author name and links it to the work."""
    for name in ol_item.get("author_name", []):
        author = await author_repo.get_author_by_name(name) or await author_repo.create_author(name=name)
        await author_repo.add_author_to_work(work_id, author.id)


async def _link_genres(genre_names: list[str], work_id: int, genre_repo: GenreRepository) -> None:
    """Gets-or-creates each Google Books category and links it to the work."""
    for name in genre_names:
        slug = _slugify(name)
        genre = await genre_repo.get_genre_by_slug(slug) or await genre_repo.create_genre(name=name, slug=slug)
        await genre_repo.add_genre_to_work(work_id, genre.id)


async def cache_work(
        ol_item: dict,
        session: AsyncSession,
        language: str = DEFAULT_LANGUAGE,
) -> Work:
    """Persists an Open Library search result as a Work with its primary Edition,
    enriched with Google Books data (cover, categories) where available.

    Deduplicates on the edition's Open Library ID: if an edition with that ID
    already exists, its parent Work is returned instead of creating a duplicate.

    Args:
        ol_item: Open Library book document.
        session: Async SQLAlchemy session. A single commit covers the Work,
            Edition, and any newly linked Author/Genre rows.
        language: Language code stored as the work's primary language and the
            edition's language (e.g. "eng", "rus", "uzb" per the catalog's
            multi-language requirement).

    Returns:
        The cached (or newly created) Work instance.
    """
    work_repo = WorkRepository(session)
    edition_repo = EditionRepository(session)
    author_repo = AuthorRepository(session)
    genre_repo = GenreRepository(session)

    open_library_id = ol_item.get("key", "")
    existing_edition = await edition_repo.get_edition_by_open_library_id(open_library_id)
    if existing_edition:
        return await work_repo.get_work_by_id(existing_edition.work_id)

    async with httpx.AsyncClient() as client:
        google_data = await fetch_from_google(ol_item, client)

    cover_url = None
    description = None
    genre_names: list[str] = []
    google_id = None

    if google_data:
        google_id = google_data.get("id")
        info = google_data.get("volumeInfo", {})
        cover_url = info.get("imageLinks", {}).get("thumbnail")
        genre_names = info.get("categories", [])
        description = info.get("description")

    if not description:
        description = ol_item.get("description")

    if not cover_url and ol_item.get("cover_i"):
        cover_url = f"https://covers.openlibrary.org/b/id/{ol_item['cover_i']}-L.jpg"

    isbn_list = ol_item.get("isbn", [])
    isbn = next((i for i in isbn_list if len(i) == 13), None) or (isbn_list[0] if isbn_list else None)
    title = ol_item.get("title", "")

    work = await work_repo.create_work(
        canonical_title=title,
        description=description,
        primary_language=language,
    )
    await edition_repo.create_edition(
        work_id=work.id,
        title=title,
        language=language,
        google_books_id=google_id or f"ol:{open_library_id}",
        open_library_id=open_library_id,
        published_year=ol_item.get("first_publish_year"),
        pages_count=ol_item.get("number_of_pages_median"),
        isbn=isbn,
        cover_url=cover_url,
        is_primary=True,
    )

    await _link_authors(ol_item, work.id, author_repo)
    await _link_genres(genre_names, work.id, genre_repo)

    await session.commit()
    return work
