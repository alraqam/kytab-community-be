from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv

from src.backend.core.rate_limit import RateLimiter
from src.backend.identity.auth.dependencies import get_current_user, get_auth_manager, get_two_factor_manager
from src.backend.identity.auth.exceptions import InvalidTwoFactorCodeError, InvalidTokenError
from src.backend.identity.auth.managers.auth import AuthManager
from src.backend.identity.auth.managers.two_factor import TwoFactorManager
from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import TwoFactorSetup, TwoFactorEnable, TwoFactorRecoveryCodes, \
    TwoFactorDisable, TwoFactorVerify

router = APIRouter(
    prefix="/2fa",
    tags=["two-factor"]
)

two_factor_verify_limiter = RateLimiter("2fa-verify")

@cbv(router)
class TwoFactorRouter:
    """CBV router for two-factor authentication: setup, enable, disable, and login verification."""

    manager: TwoFactorManager = Depends(get_two_factor_manager)
    auth_manager: AuthManager = Depends(get_auth_manager)

    @router.post(
        "/setup",
        summary="starting two-factor authentication setup",
        response_model=TwoFactorSetup,
    )
    async def setup(
            self,
            user: User = Depends(get_current_user)
    ):
        """Generates a pending TOTP secret for the current user and returns its provisioning details."""
        return await self.manager.setup(user)

    @router.post(
        "/enable",
        summary="confirming and enabling two-factor authentication",
        response_model=TwoFactorRecoveryCodes,
    )
    async def enable(
            self,
            request: TwoFactorEnable,
            user: User = Depends(get_current_user)
    ):
        """Confirms the pending TOTP secret with a code and enables two-factor authentication."""
        recovery_codes = await self.manager.enable(user, request.code)
        return TwoFactorRecoveryCodes(recovery_codes=recovery_codes)

    @router.post(
        "/disable",
        summary="disabling two-factor authentication",
    )
    async def disable(
            self,
            request: TwoFactorDisable,
            user: User = Depends(get_current_user)
    ) -> None:
        """Disables two-factor authentication after verifying the user's password."""
        await self.manager.disable(user, request.password)

    @router.post(
        "/verify",
        summary="completing login with a two-factor code",
    )
    async def verify(
            self,
            request: Request,
            payload: TwoFactorVerify
    ):
        """Completes a pending login by verifying a TOTP or recovery code."""
        rate_limit_key = f"{request.client.host}:{payload.pre_auth_token}"
        await two_factor_verify_limiter.check(rate_limit_key)
        try:
            response = await self.auth_manager.verify_two_factor(payload.pre_auth_token, payload.code, request)
        except (InvalidTwoFactorCodeError, InvalidTokenError):
            await two_factor_verify_limiter.record_failure(rate_limit_key)
            raise
        await two_factor_verify_limiter.reset(rate_limit_key)
        return response
