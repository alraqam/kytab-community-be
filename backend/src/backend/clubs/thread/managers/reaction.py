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
from src.backend.core.storage import StorageService
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType

class PostReactionManager:
    """Handles business logic for reactions on posts: creation, deletion, retrieval, and reaction notifications."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """Initializes the manager and its dependent repositories and managers.

        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.reaction_repo = PostReactionRepository(session)
        self.club_manager = ClubManager(session, StorageService())
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
        """Creates a reaction on a post and notifies the post's author.

        Args:
            user: User creating the reaction.
            club: Club the post's thread belongs to.
            post: Post instance being reacted to.
            request: CreatePostReaction payload with the emoji.

        Returns:
            Newly created PostReaction instance.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
            PostReactionAlreadyExists: When the user has already reacted to the post with the same emoji.
        """
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
        """Deletes a reaction owned by the given user.

        Args:
            user: User requesting the deletion; must own the reaction.
            reaction: PostReaction instance to delete.

        Raises:
            IsNotPostReactionOwnerError: When the user did not create the reaction.
        """
        await is_reaction_owner(reaction, user)

        await self.reaction_repo.delete_reaction(
            reaction=reaction,
        )
        await self.session.commit()

    async def get_post_reactions(
            self,
            post: Post,
    ) -> list[PostReaction]:
        """Lists all reactions on a post.

        Args:
            post: Post instance to list reactions for.

        Returns:
            List of PostReaction instances on the post.
        """
        reactions = await self.reaction_repo.get_post_reactions(
            post_id=post.id,
        )
        return reactions

    async def get_reaction_by_id(
            self,
            reaction_id: int,
    ) -> PostReaction:
        """Fetches a reaction by ID.

        Args:
            reaction_id: ID of the reaction to fetch.

        Returns:
            Matching PostReaction instance.

        Raises:
            ReactionNotFoundError: When no reaction with the given ID exists.
        """
        reaction = await self.reaction_repo.get_reaction_by_id(
            reaction_id=reaction_id,
        )
        if not reaction:
            raise ReactionNotFoundError("Reaction not found")
        return reaction
