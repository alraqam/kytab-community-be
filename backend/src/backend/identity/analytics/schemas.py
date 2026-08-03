from pydantic import BaseModel


class GenreBreakdown(BaseModel):
    genre: str
    books_read: int

class MonthlyReadingActivity(BaseModel):
    month: str
    books_finished: int
    pages_read: int

class GetUserAnalytics(BaseModel):
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
    month: str
    signups: int

class GetPlatformUserAnalytics(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    admin_count: int
    librarian_count: int
    weekly_active_users: int
    monthly_active_users: int
    signups_by_month: list[SignupsByMonth]
