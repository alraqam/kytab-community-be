from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.follow.managers import FollowManager
from src.backend.core.services import is_valid_url
from src.backend.identity.auth.models import User
from src.backend.identity.auth.services.security import PasswordService
from src.backend.identity.profile.exceptions import ProfileNotFoundError, PrivateProfileError, InvalidAvatarUrlError, \
    InvalidLinkUrlError
from src.backend.identity.profile.models import Profile
from src.backend.identity.profile.repository import ProfileRepository
from src.backend.identity.profile.schemas import CreateProfile, ProfileVisibilityEnum, UpdateProfileAvatar, \
    UpdateProfile, UpdateProfileVisibility
from src.backend.identity.users.repository import UserRepository


class ProfileManager:
    """Handles business logic for user profile management."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.profile_repo = ProfileRepository(session)
        self.user_repo = UserRepository(session)
        self.password_service = PasswordService()
        self.follow_manager = FollowManager(session)

    async def create(
            self,
            request: CreateProfile
    ) -> Profile:
        """Creates a new profile for a user.

        Args:
            request: CreateProfile payload with user_id and fullname.

        Returns:
            Newly created Profile instance.
        """
        profile = await self.profile_repo.create(request.user_id, request.fullname)
        return profile

    async def get_profile_by_user(
            self,
            user: User
    ) -> Profile:
        """Fetches the profile belonging to the given user.

        Args:
            user: User whose profile to fetch.

        Returns:
            Matching Profile instance.

        Raises:
            ProfileNotFoundError: When the user has no profile.
        """
        profile = await self.profile_repo.get_profile_by_user(user.id)
        if not profile:
            raise ProfileNotFoundError("Profile not found")
        return profile

    async def get_profile(
            self,
            user: User,
            get_user: User
    ) -> Profile:
        """Fetches another user's profile, enforcing visibility rules.

        Args:
            user: User requesting to view the profile.
            get_user: User whose profile is being requested.

        Returns:
            Matching Profile instance.

        Raises:
            PrivateProfileError: When the profile's visibility is private.
        """
        profile = await self.get_profile_by_user(get_user)
        if profile.visibility == ProfileVisibilityEnum.private:
            raise PrivateProfileError("Private profile error")

        if profile.visibility == ProfileVisibilityEnum.followers_only:
            await self.follow_manager.is_following_user(user.id, profile.user_id)
        return profile

    async def update_avatar(
            self,
            user: User,
            request: UpdateProfileAvatar
    ) -> None:
        """Updates the current user's avatar URL after validating its format.

        Args:
            user: User whose avatar to update.
            request: UpdateProfileAvatar payload with the new avatar_url.

        Raises:
            InvalidAvatarUrlError: When avatar_url is not a valid HTTP/HTTPS URL.
        """
        profile = await self.get_profile_by_user(user)

        if not is_valid_url(request.avatar_url):
            raise InvalidAvatarUrlError("Invalid url format")

        await self.profile_repo.update_avatar(
            profile=profile,
            avatar=request.avatar_url
        )
        await self.session.commit()

    async def update_profile(
            self,
            user: User,
            request: UpdateProfile
    ) -> None:
        """Updates the current user's profile fields after validating link URLs.

        Args:
            user: User whose profile to update.
            request: UpdateProfile payload with the fields to change.

        Raises:
            InvalidLinkUrlError: When any provided link is not a valid HTTP/HTTPS URL.
        """
        profile = await self.get_profile_by_user(user)

        if any(not is_valid_url(link) for link in request.links or ()):
            raise InvalidLinkUrlError("Invalid link url")


        await self.profile_repo.update_profile(
            profile=profile,
            fullname=request.fullname,
            bio=request.bio,
            favorite_genres=request.favorite_genres,
            links=request.links,
        )
        await self.session.commit()

    async def update_visibility(
            self,
            user: User,
            request: UpdateProfileVisibility
    ) -> None:
        """Updates the current user's profile visibility setting.

        Args:
            user: User whose profile visibility to update.
            request: UpdateProfileVisibility payload with the new visibility value.
        """
        profile = await self.get_profile_by_user(user)

        await self.profile_repo.update_visibility(
            profile=profile,
            visibility=request.visibility
        )
        await self.session.commit()
