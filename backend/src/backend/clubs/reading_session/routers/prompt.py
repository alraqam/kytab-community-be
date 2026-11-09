from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies.reading_session import get_reading_session_or_404, get_milestone_or_404, \
    get_discussion_prompt_manager, get_discussion_prompt_or_404
from src.backend.clubs.reading_session.managers.prompt import DiscussionPromptManager
from src.backend.clubs.reading_session.models.reading_session import ReadingSession, Milestone, DiscussionPrompt
from src.backend.clubs.reading_session.schemas.reading_session import GetDiscussionPrompt, CreateDiscussionPrompt, \
    UpdateDiscussionPrompt
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{milestone_id}/prompt",
    tags=["discussion_prompts"]
)

@cbv(router)
class DiscussionPromptRouter:
    """CBV router for managing discussion prompts on a milestone: create, update, delete, and list."""

    manager: DiscussionPromptManager = Depends(get_discussion_prompt_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    session: ReadingSession = Depends(get_reading_session_or_404)
    milestone: Milestone = Depends(get_milestone_or_404)

    @router.post(
        "/",
        summary="creating discussion prompt",
        response_model=GetDiscussionPrompt,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404),
    )
    async def create_prompt(
            self,
            request: CreateDiscussionPrompt
    ):
        """Creates a new discussion prompt for the milestone."""
        result = await self.manager.create_prompt(self.user, self.club, self.milestone, request)
        return result

    @router.put(
        "/{prompt_id}",
        summary="update discussion prompt",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_prompt(
            self,
            request: UpdateDiscussionPrompt,
            prompt: DiscussionPrompt = Depends(get_discussion_prompt_or_404),
    ):
        """Updates a discussion prompt's text."""
        await self.manager.update_prompt(self.user, self.club, prompt, request)

    @router.delete(
        "/{prompt_id}",
        summary="deleting discussion prompt",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_prompt(
            self,
            prompt: DiscussionPrompt = Depends(get_discussion_prompt_or_404)
    ):
        """Deletes a discussion prompt."""
        await self.manager.delete_prompt(self.user, self.club, prompt)

    @router.get(
        "/",
        summary="getting milestone discussion prompts",
        response_model=list[GetDiscussionPrompt],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_milestone_prompts(
            self,
    ):
        """Lists all discussion prompts for the milestone."""
        result = await self.manager.get_milestone_prompts(self.user, self.club, self.milestone)
        return result
