from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.thread.dependencies import is_reaction_owner
from src.backend.clubs.thread.exceptions import ReactionNotFoundError, PostReactionAlreadyExists
from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models import PostReaction, Post
from src.backend.clubs.thread.repository.reaction import PostReactionRepository
from src.backend.clubs.thread.schemas import CreatePostReaction
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType

class PostReactionManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.reaction_repo = PostReactionRepository(session)
        self.club_manager = ClubManager(session)
        self.thread_manager = ThreadManager(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def create_reaction(
            self,
            user: User,
            club: Club,
            post: Post,
            request: CreatePostReaction
    ) -> PostReaction:
        await is_club_member(club, user, self.session)

        try:
            response = await self.reaction_repo.create_reaction(
                post_id=post.id,
                user_id=user.id,
                emoji=request.emoji
            )
        except IntegrityError:
            raise PostReactionAlreadyExists("Reaction for this post already exists")
        await self.session.commit()

        if post.author_id != user.id:
            author = await self.user_manager.get_user_by_id(post.author_id)
            await self.notification_manager.notify(
                author,
                category=NotificationCategory.general,
                title=f"{user.username} reacted {request.emoji} to your post",
                object_type=NotificationObjectType.post,
                object_id=post.id,
                club_id=club.id,
            )
        return response


    async def delete_reaction(
            self,
            user: User,
            reaction: PostReaction,
    ) -> None:
        await is_reaction_owner(reaction, user)

        await self.reaction_repo.delete_reaction(
            reaction=reaction,
        )
        await self.session.commit()

    async def get_post_reactions(
            self,
            post: Post,
    ) -> list[PostReaction]:
        reactions = await self.reaction_repo.get_post_reactions(
            post_id=post.id,
        )
        return reactions

    async def get_reaction_by_id(
            self,
            reaction_id: int,
    ) -> PostReaction:
        reaction = await self.reaction_repo.get_reaction_by_id(
            reaction_id=reaction_id,
        )
        if not reaction:
            raise ReactionNotFoundError("Reaction not found")
        return reaction