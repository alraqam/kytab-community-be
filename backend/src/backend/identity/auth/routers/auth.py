from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from jose.exceptions import ExpiredSignatureError, JWTError

from src.backend.identity.auth.dependencies import get_auth_manager, get_current_user
from src.backend.identity.auth.exceptions import InvalidTokenError, LinkExpiredError
from src.backend.identity.auth.managers.auth import AuthManager
from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import UserRegister, ChangeUserPassword, ResetPassword, UpdateUser, RefreshToken
from src.backend.identity.auth.services.email import decode_verification_token
from src.backend.identity.users.dependencies import get_user_manager

from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.schemas import UpdateUserVerification

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@cbv(router)
class AuthRouter:
    """CBV router for authentication endpoints: login, register, me, and token refresh."""

    manager: AuthManager = Depends(get_auth_manager)
    user_manager: UserManager = Depends(get_user_manager)

    @router.post(
        "/login",
        summary="authorization to the system"
    )
    async def login(
            self,
            request: Request,
            form_data: OAuth2PasswordRequestForm = Depends()
    ):
        """Authenticates a user and returns an access/refresh token pair.

        Args:
            form_data: OAuth2 form with username and password.
        """
        response = await self.manager.login(form_data.username, form_data.password, request)
        return response

    @router.post(
        "/register",
        summary="user registration"
    )
    async def register(
            self,
            request: UserRegister
    ):
        """Registers a new user account.

        Args:
            request: UserRegister payload with username, email, and password.
        """
        response = await self.manager.register(request)
        return response

    @router.post(
        "/logout",
        summary = "logging out from the system"
    )
    async def logout_route(
            self,
            request: RefreshToken,
    ):
        await self.manager.logout(request.refresh_token)


    @router.get(
        "/verify-email",
        summary="verifying email")
    async def verify_email(
            self,
            token: str
    ):
        try:
            user_id = decode_verification_token(token)
        except ExpiredSignatureError:
            raise LinkExpiredError("Verification link expired")
        except JWTError:
            raise InvalidTokenError(400, "Invalid verification token")

        await self.user_manager.update_verification(
            user_id,
            UpdateUserVerification(is_verified=True)
        )
        return {"message": "Email verified"}

    @router.get(
        "/me",
        summary="getting current user"
    )
    async def get_me(
            self,
            user: User = Depends(get_current_user)
    ):
        """Returns the profile of the currently authenticated user."""
        return user

    @router.post(
        "/refresh",
        summary="refresh token",
    )
    async def refresh(
            self,
            request: RefreshToken
    ):
        """Issues a new token pair using the provided refresh token.

        Args:
            request: RefreshToken payload containing the refresh token.
        """
        response = await self.manager.refresh_token(request.refresh_token)
        return response

    @router.delete(
        "/delete",
        summary="delete account",
    )
    async def delete_user(
            self,
            user: User = Depends(get_current_user)
    ):
        await self.user_manager.delete_user(user)
        return user

    @router.put(
        "/password",
        summary="updating password"
    )
    async def change_password(
            self,
            request: ChangeUserPassword,
            user: User = Depends(get_current_user)
    ) -> None:
        """Changes the current user's password.

        Args:
            request: ChangeUserPassword payload with old_password and new_password.
        """
        await self.manager.change_password(user, request)

    @router.put(
        "/info",
        summary="updating current user information"
    )
    async def update_user(
            self,
            request: UpdateUser,
            user: User = Depends(get_current_user)
    ) -> None:
        """Updates the current user's username, fullname, and email.

        Args:
            request: UpdateUser payload with new profile fields.
        """
        await self.manager.update(user, request)

    @router.post(
        "/forgot-password",
        summary="sending email for resetting password"
    )
    async def forgot_password(
            self,
            user: User = Depends(get_current_user)
    ):
        result = await self.manager.forgot_password(user)
        return result

    @router.post(
        "/reset-password",
        summary="resetting password"
    )
    async def reset_password(
            self,
            request: ResetPassword
    ):
        await self.manager.reset_password(request)