import csv
import io
import zipfile
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.repository.posts import PostRepository
from src.backend.identity.auth.models import User
from src.backend.library.progress.repositories.progress_logs import ProgressLogRepository
from src.backend.library.progress.repositories.reading_period import ReadingPeriodRepository
from src.backend.library.reviews.repositories.review import ReviewRepository
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.repositories.shelf_item import ShelfItemRepository
from src.backend.trust_safety.export.schemas import ClubPostExport, ProgressLogExport, ReadingPeriodExport, \
    ReviewExport, ShelfItemExport, UserDataExport


class DataExportManager:
    """Builds a GDPR self-service export of a user's library, reviews, progress, and club posts."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.shelf_manager = ShelfManager(session)
        self.shelf_item_repo = ShelfItemRepository(session)
        self.reading_period_repo = ReadingPeriodRepository(session)
        self.progress_log_repo = ProgressLogRepository(session)
        self.review_repo = ReviewRepository(session)
        self.post_repo = PostRepository(session)

    async def build_user_data_export(
            self,
            user: User,
    ) -> UserDataExport:
        """Collects a user's exportable personal data from across the library and club domains.

        Args:
            user: User whose data is being exported.

        Returns:
            UserDataExport bundling the user's shelf items, reviews, reading periods,
            progress logs, and club posts.
        """
        shelves = await self.shelf_manager.get_my_shelves(user)
        shelf_items = []
        for shelf in shelves:
            for item in await self.shelf_item_repo.get_shelf_items(shelf.id):
                shelf_items.append(
                    ShelfItemExport(
                        shelf_name=shelf.name,
                        work_title=item.work_title,
                        edition_title=item.edition_title,
                        added_at=item.created_at,
                    )
                )

        reviews = [
            ReviewExport(
                work_title=review.work_title,
                rating=review.rating,
                text=review.text,
                contains_spoiler=review.contains_spoiler,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in await self.review_repo.get_user_reviews(user.id)
        ]

        reading_periods = [
            ReadingPeriodExport(
                work_title=period.work_title,
                started_at=period.started_at,
                finished_at=period.finished_at,
            )
            for period in await self.reading_period_repo.get_user_reading_periods(user.id)
        ]

        progress_logs = [
            ProgressLogExport(
                period_id=log.period_id,
                pages_read=log.pages_read,
                log_date=log.log_date,
                note=log.note,
            )
            for log in await self.progress_log_repo.get_user_progress_logs(user.id)
        ]

        club_posts = [
            ClubPostExport(
                thread_title=post.thread_title,
                title=post.title,
                body=post.body,
                is_spoiler=post.is_spoiler,
                created_at=post.created_at,
            )
            for post in await self.post_repo.get_user_posts(user.id)
        ]

        return UserDataExport(
            user_id=user.id,
            username=user.username,
            email=user.email,
            generated_at=datetime.now(timezone.utc),
            shelf_items=shelf_items,
            reviews=reviews,
            reading_periods=reading_periods,
            progress_logs=progress_logs,
            club_posts=club_posts,
        )

    async def build_export_archive(
            self,
            user: User,
    ) -> bytes:
        """Packages a user's data export as a ZIP archive containing JSON and per-section CSV files.

        Args:
            user: User whose data is being exported.

        Returns:
            Bytes of the ZIP archive.
        """
        export = await self.build_user_data_export(user)

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("data.json", export.model_dump_json(indent=2))
            archive.writestr("shelf_items.csv", _to_csv(export.shelf_items))
            archive.writestr("reviews.csv", _to_csv(export.reviews))
            archive.writestr("reading_periods.csv", _to_csv(export.reading_periods))
            archive.writestr("progress_logs.csv", _to_csv(export.progress_logs))
            archive.writestr("club_posts.csv", _to_csv(export.club_posts))

        return buffer.getvalue()


def _to_csv(rows: list) -> str:
    """Renders a list of Pydantic models as CSV text.

    Args:
        rows: List of Pydantic model instances sharing the same fields.

    Returns:
        CSV text with a header row, or just the header-less empty string if rows is empty.
    """
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].model_fields.keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow(row.model_dump())
    return output.getvalue()
