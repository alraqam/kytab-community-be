from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.repository.genre import GenreRepository
from src.backend.identity.analytics.schemas import GenreBreakdown, GetPlatformUserAnalytics, GetUserAnalytics, \
    MonthlyReadingActivity, SignupsByMonth
from src.backend.identity.auth.models import User
from src.backend.identity.auth.repository import SessionRepository
from src.backend.identity.auth.schemas import UserRoleEnum
from src.backend.identity.follow.managers import FollowManager
from src.backend.identity.profile.managers import ProfileManager
from src.backend.identity.users.repository import UserRepository
from src.backend.library.progress.managers.reading_period import ReadingPeriodManager
from src.backend.library.progress.repositories.progress_logs import ProgressLogRepository
from src.backend.library.reading_goals.repository import ReadingGoalRepository
from src.backend.library.reviews.repositories.review import ReviewRepository
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.repositories.shelf_item import ShelfItemRepository
from src.backend.library.shelf.schemas import ShelfDefault


class UserAnalyticsManager:
    """Aggregates personal reading stats and platform-wide user metrics from existing domain data."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.shelf_manager = ShelfManager(session)
        self.shelf_item_repo = ShelfItemRepository(session)
        self.reading_period_manager = ReadingPeriodManager(session)
        self.progress_log_repo = ProgressLogRepository(session)
        self.review_repo = ReviewRepository(session)
        self.goal_repo = ReadingGoalRepository(session)
        self.follow_manager = FollowManager(session)
        self.genre_repo = GenreRepository(session)
        self.profile_manager = ProfileManager(session)

    async def get_user_analytics(
            self,
            user: User,
            current_user: User,
    ) -> GetUserAnalytics:
        if user.id != current_user.id:
            await self.profile_manager.get_profile(current_user, user)

        shelves = await self.shelf_manager.get_my_shelves(user)
        shelves_by_name = {shelf.name: shelf for shelf in shelves}

        shelf_items_by_default = {}
        for default_shelf in ShelfDefault:
            shelf = shelves_by_name.get(default_shelf)
            shelf_items_by_default[default_shelf] = (
                await self.shelf_item_repo.get_shelf_items(shelf.id) if shelf else []
            )
        read_items = shelf_items_by_default[ShelfDefault.read]

        genre_counter = Counter()
        for item in read_items:
            genres = await self.genre_repo.get_genres_for_work(item.work_id)
            genre_counter.update(genre.name for genre in genres)

        periods = await self.reading_period_manager.get_my_reading_periods(user)
        finished_periods = [period for period in periods if period.finished_at is not None]

        durations = [
            (period.finished_at - period.started_at).days
            for period in finished_periods if period.started_at
        ]
        longest_read_days = max(durations) if durations else None
        shortest_read_days = min(durations) if durations else None

        current_year = datetime.now(timezone.utc).year
        current_year_books_read = sum(
            1 for period in finished_periods if period.finished_at.year == current_year
        )

        books_by_month = Counter(period.finished_at.strftime("%Y-%m") for period in finished_periods)

        logs = await self.progress_log_repo.get_user_progress_logs(user.id)
        pages_by_month = defaultdict(int)
        for log in logs:
            pages_by_month[log.log_date.strftime("%Y-%m")] += log.pages_read

        months = sorted(set(books_by_month) | set(pages_by_month))
        monthly_activity = [
            MonthlyReadingActivity(
                month=month,
                books_finished=books_by_month.get(month, 0),
                pages_read=pages_by_month.get(month, 0),
            )
            for month in months
        ]

        reviews = await self.review_repo.get_user_reviews(user.id)
        ratings = [review.rating for review in reviews if review.rating is not None]
        average_rating_given = sum(ratings) / len(ratings) if ratings else None

        goals = await self.goal_repo.get_user_goals(user.id)
        current_goal = next((goal for goal in goals if goal.year == current_year), None)

        followers = await self.follow_manager.get_user_followers(user)
        followings = await self.follow_manager.get_user_followings(user)

        return GetUserAnalytics(
            user_id=user.id,
            want_to_read_count=len(shelf_items_by_default[ShelfDefault.want_to_read]),
            currently_reading_count=len(shelf_items_by_default[ShelfDefault.currently_reading]),
            read_count=len(read_items),
            did_not_finish_count=len(shelf_items_by_default[ShelfDefault.did_not_finish]),
            reviews_written=len(reviews),
            average_rating_given=average_rating_given,
            longest_read_days=longest_read_days,
            shortest_read_days=shortest_read_days,
            current_year_books_read=current_year_books_read,
            current_year_goal_target=current_goal.target_count if current_goal else None,
            followers_count=len(followers),
            following_count=len(followings),
            genre_breakdown=[
                GenreBreakdown(genre=genre, books_read=count)
                for genre, count in genre_counter.most_common()
            ],
            monthly_activity=monthly_activity,
        )

    async def get_platform_analytics(self) -> GetPlatformUserAnalytics:
        users = await self.user_repo.get_all_users(None)

        role_counts = Counter(user.role for user in users)
        verified_count = sum(1 for user in users if user.is_verified)
        active_count = sum(1 for user in users if user.is_active and not user.is_deleted)
        signups = Counter(user.created_at.strftime("%Y-%m") for user in users if user.created_at)

        now = datetime.now(timezone.utc)
        week_cutoff = now - timedelta(days=7)
        month_cutoff = now - timedelta(days=30)

        weekly_active = 0
        monthly_active = 0
        for user in users:
            sessions = await self.session_repo.get_user_active_sessions(user.id)
            if not sessions:
                continue
            last_active = max(session.last_active_at for session in sessions)
            if last_active.tzinfo is None:
                last_active = last_active.replace(tzinfo=timezone.utc)
            if last_active >= week_cutoff:
                weekly_active += 1
            if last_active >= month_cutoff:
                monthly_active += 1

        return GetPlatformUserAnalytics(
            total_users=len(users),
            active_users=active_count,
            verified_users=verified_count,
            admin_count=role_counts.get(UserRoleEnum.admin, 0),
            librarian_count=role_counts.get(UserRoleEnum.librarian, 0),
            weekly_active_users=weekly_active,
            monthly_active_users=monthly_active,
            signups_by_month=[
                SignupsByMonth(month=month, signups=count)
                for month, count in sorted(signups.items())
            ],
        )
