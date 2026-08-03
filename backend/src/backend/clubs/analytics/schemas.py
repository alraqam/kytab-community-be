from pydantic import BaseModel


class ClubModerationSummary(BaseModel):
    pending_join_requests: int
    pending_complaints: int
    total_complaints: int

class MemberRoleBreakdown(BaseModel):
    owner: int
    moderator: int
    member: int

class MonthlyCount(BaseModel):
    month: str
    count: int

class GetClubAnalytics(BaseModel):
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
    total_clubs: int
    active_clubs: int
    archived_clubs: int
    public_clubs: int
    private_clubs: int
    secret_clubs: int
    total_memberships: int
    clubs_created_by_month: list[MonthlyCount]
