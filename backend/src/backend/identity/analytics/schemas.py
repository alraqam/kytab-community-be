from pydantic import BaseModel


class GenreBreakdown(BaseModel):
    """Response payload representing a count of finished books for a given genre."""

    genre: str
    books_read: int

class MonthlyReadingActivity(BaseModel):
    """Response payload representing a user's reading activity for a given month."""

    month: str
    books_finished: int
    pages_read: int

class GetUserAnalytics(BaseModel):
    """Response payload representing a user's personal reading analytics overview."""

    user_id: int
    want_to_read_count: int
    currently_reading_count: int
    read_count: int
    did_not_finish_count: int
    reviews_written: int
    average_rating_given: float | None
    longest_read_days: int | None
    shortest_read_days: int | None
    current_year_books_read: int
    current_year_goal_target: int | None
    followers_count: int
    following_count: int
    genre_breakdown: list[GenreBreakdown]
    monthly_activity: list[MonthlyReadingActivity]

class SignupsByMonth(BaseModel):
    """Response payload representing a count of user signups for a given month."""

    month: str
    signups: int

class GetPlatformUserAnalytics(BaseModel):
    """Response payload representing platform-wide user analytics."""

    total_users: int
    active_users: int
    verified_users: int
    admin_count: int
    librarian_count: int
    weekly_active_users: int
    monthly_active_users: int
    signups_by_month: list[SignupsByMonth]
