from pydantic import BaseModel


class ClubModerationSummary(BaseModel):
    """Response payload summarizing a club's pending join requests and complaints."""

    pending_join_requests: int
    pending_complaints: int
    total_complaints: int

class MemberRoleBreakdown(BaseModel):
    """Response payload breaking down a club's member count by role."""

    owner: int
    moderator: int
    member: int

class MonthlyCount(BaseModel):
    """Response payload representing a count of items for a given month."""

    month: str
    count: int

class GetClubAnalytics(BaseModel):
    """Response payload representing a club's analytics overview."""

    club_id: int
    total_members: int
    role_breakdown: MemberRoleBreakdown
    member_growth: list[MonthlyCount]
    general_threads_count: int
    general_posts_count: int
    active_reading_sessions: int
    completed_reading_sessions: int
    average_milestone_completion: float | None
    polls_count: int
    events_count: int
    upcoming_events_count: int

class GetPlatformClubAnalytics(BaseModel):
    """Response payload representing platform-wide club analytics."""

    total_clubs: int
    active_clubs: int
    archived_clubs: int
    public_clubs: int
    private_clubs: int
    secret_clubs: int
    total_memberships: int
    clubs_created_by_month: list[MonthlyCount]
