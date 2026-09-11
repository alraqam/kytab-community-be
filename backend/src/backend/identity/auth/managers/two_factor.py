from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.exceptions import TwoFactorAlreadyEnabledError, TwoFactorNotEnabledError, \
    TwoFactorSetupNotStartedError, InvalidTwoFactorCodeError, InvalidUsernameOrPasswordError
from src.backend.identity.auth.models import User
from src.backend.identity.auth.repository import RecoveryCodeRepository
from src.backend.identity.auth.schemas import TwoFactorSetup
from src.backend.identity.auth.services.security import PasswordService, hash_token
from src.backend.identity.auth.services.two_factor import TOTPService, generate_recovery_codes
from src.backend.identity.users.repository import UserRepository


class TwoFactorManager:
    """Handles two-factor authentication business logic: setup, enable, disable, and code verification."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.recovery_code_repo = RecoveryCodeRepository(session)
        self.totp_service = TOTPService()
        self.password_service = PasswordService()

    async def setup(
            self,
            user: User
    ) -> TwoFactorSetup:
        """Generates a new pending TOTP secret for the user.

        Args:
            user: Authenticated user requesting two-factor setup.

        Returns:
            TwoFactorSetup with the secret and its provisioning URI.

        Raises:
            TwoFactorAlreadyEnabledError: When two-factor authentication is already active.
        """
        if user.is_2fa_enabled:
            raise TwoFactorAlreadyEnabledError("Two-factor authentication is already enabled")

        secret = self.totp_service.generate_secret()
        await self.user_repo.update_totp_secret(user, secret)
        await self.session.commit()
        return TwoFactorSetup(
            secret=secret,
            provisioning_uri=self.totp_service.provisioning_uri(secret, user.email),
        )

    async def enable(
            self,
            user: User,
            code: str
    ) -> list[str]:
        """Confirms the pending TOTP secret and activates two-factor authentication.

        Args:
            user: Authenticated user enabling two-factor authentication.
            code: TOTP code generated from the pending secret.

        Returns:
            Newly generated plain-text recovery codes; shown to the user only once.

        Raises:
            TwoFactorAlreadyEnabledError: When two-factor authentication is already active.
            TwoFactorSetupNotStartedError: When no pending secret exists for the user.
            InvalidTwoFactorCodeError: When the code does not match the pending secret.
        """
        if user.is_2fa_enabled:
            raise TwoFactorAlreadyEnabledError("Two-factor authentication is already enabled")

        if not user.totp_secret:
            raise TwoFactorSetupNotStartedError("Two-factor setup has not been started")

        if not self.totp_service.verify(user.totp_secret, code):
            raise InvalidTwoFactorCodeError("Invalid two-factor code")

        await self.user_repo.update_2fa_enabled(user, True)
        recovery_codes = generate_recovery_codes()
        await self.recovery_code_repo.create_many(
            user.id,
            [hash_token(code) for code in recovery_codes],
        )
        await self.session.commit()
        return recovery_codes

    async def disable(
            self,
            user: User,
            password: str
    ) -> None:
        """Disables two-factor authentication and clears its secret and recovery codes.

        Args:
            user: Authenticated user disabling two-factor authentication.
            password: Current account password, required as confirmation.

        Raises:
            TwoFactorNotEnabledError: When two-factor authentication is not active.
            InvalidUsernameOrPasswordError: When the password does not match.
        """
        if not user.is_2fa_enabled:
            raise TwoFactorNotEnabledError("Two-factor authentication is not enabled")

        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidUsernameOrPasswordError("Invalid username or password")

        await self.user_repo.update_2fa_enabled(user, False)
        await self.user_repo.update_totp_secret(user, None)
        await self.recovery_code_repo.delete_all_for_user(user.id)
        await self.session.commit()

    async def verify_code(
            self,
            user: User,
            code: str
    ) -> bool:
        """Checks a code against the user's TOTP secret, falling back to unused recovery codes.

        A matched recovery code is consumed and cannot be reused.

        Args:
            user: User completing a pending login.
            code: TOTP code or recovery code entered by the user.

        Returns:
            True if the code is valid, False otherwise.
        """
        if user.totp_secret and self.totp_service.verify(user.totp_secret, code):
            return True

        code_hash = hash_token(code)
        recovery_codes = await self.recovery_code_repo.get_unused_by_user(user.id)
        for recovery_code in recovery_codes:
            if recovery_code.code_hash == code_hash:
                await self.recovery_code_repo.mark_used(recovery_code)
                await self.session.commit()
                return True

        return False
