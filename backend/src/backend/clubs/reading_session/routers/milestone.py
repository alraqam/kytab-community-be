from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies import get_reading_session_or_404
from src.backend.clubs.reading_session.filters import MilestoneFilter
from src.backend.clubs.reading_session.dependencies import get_milestone_manager, get_milestone_or_404
from src.backend.clubs.reading_session.managers.milestone import MilestoneManager
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.reading_session.schemas import GetMilestone, CreateMilestone, UpdateMilestone
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{session_id}/milestone",
    tags=["milestones"]
)

@cbv(router)
class MilestoneRouter:
    manager: MilestoneManager = Depends(get_milestone_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    session: ReadingSession = Depends(get_reading_session_or_404)

    @router.post(
        "/",
        summary="creating milestone",
        response_model=GetMilestone
    )
    async def create_milestone(
            self,
            request: CreateMilestone
    ):
        result = await self.manager.create_milestone(self.user, self.session, request)
        return result

    @router.put(
        "/{milestone_id}",
        summary="update milestone",
    )
    async def update_milestone(
            self,
            request: UpdateMilestone,
            milestone: Milestone = Depends(get_milestone_or_404),
    ):
        await self.manager.update_milestone(self.user, self.session, milestone, request)

    @router.delete(
        "/{milestone_id}",
        summary="deleting milestone",
    )
    async def delete_milestone(
            self,
            milestone: Milestone = Depends(get_milestone_or_404)
    ):
        await self.manager.delete_milestone(self.user, self.session, milestone)

    @router.get(
        "/",
        summary="getting session milestones",
        response_model=list[GetMilestone]
    )
    async def get_session_milestones(
            self,
            filters: MilestoneFilter = FilterDepends(MilestoneFilter),
    ):
        result = await self.manager.get_session_milestones(self.session, self.club, self.user, filters)
        return result

    @router.get(
        "/{milestone_id}",
        summary="getting milestone by id",
        response_model=GetMilestone
    )
    async def get_milestone_by_id(
            self,
            milestone: Milestone = Depends(get_milestone_or_404),
    ):
        return milestone