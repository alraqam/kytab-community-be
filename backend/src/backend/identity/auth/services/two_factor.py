import secrets

import pyotp

TOTP_ISSUER = "BookClub"
RECOVERY_CODE_COUNT = 10


class TOTPService:
    """Handles TOTP secret generation, provisioning URIs, and code verification."""

    def generate_secret(self) -> str:
        """Generates a new random base32 TOTP secret.

        Returns:
            Random base32-encoded secret string.
        """
        return pyotp.random_base32()

    def provisioning_uri(
            self,
            secret: str,
            email: str
    ) -> str:
        """Builds an otpauth:// URI for provisioning an authenticator app.

        Args:
            secret: Base32-encoded TOTP secret.
            email: Account email, shown as the entry's label in the authenticator app.

        Returns:
            otpauth:// provisioning URI string.
        """
        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=TOTP_ISSUER)

    def verify(
            self,
            secret: str,
            code: str
    ) -> bool:
        """Verifies a TOTP code against a secret, allowing for small clock drift.

        Args:
            secret: Base32-encoded TOTP secret.
            code: Code entered by the user.

        Returns:
            True if the code is valid, False otherwise.
        """
        return pyotp.TOTP(secret).verify(code, valid_window=1)


def generate_recovery_codes(count: int = RECOVERY_CODE_COUNT) -> list[str]:
    """Generates a batch of single-use recovery codes.

    Args:
        count: Number of recovery codes to generate.

    Returns:
        List of plain-text recovery code strings.
    """
    return [f"{secrets.token_hex(5)}" for _ in range(count)]
