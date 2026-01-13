"""PyiCloud wrapper with session management and 2FA handling."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from hidemyemail.auth.keychain import KeychainManager
from hidemyemail.core.exceptions import (
    AuthenticationError,
    CredentialsNotFoundError,
    TwoFactorRequiredError,
)

if TYPE_CHECKING:
    from pyicloud import PyiCloudService


class ICloudClient:
    """Wrapper for PyiCloud with session caching and 2FA support."""

    COOKIE_DIR = Path.home() / ".hidemyemail" / "session"

    def __init__(self) -> None:
        self.keychain = KeychainManager()
        self._api: PyiCloudService | None = None
        self._username: str | None = None

    @property
    def api(self) -> PyiCloudService:
        """Get authenticated PyiCloud API instance."""
        if self._api is None:
            raise AuthenticationError(
                "Not authenticated. Run 'hide-my-email setup' first."
            )
        return self._api

    @property
    def hidemyemail(self):
        """Access Hide My Email service."""
        return self.api.hidemyemail

    def authenticate(
        self,
        username: str,
        password: str | None = None,
        twofa_callback: Callable[[], str] | None = None,
    ) -> bool:
        """
        Authenticate with iCloud.

        Args:
            username: Apple ID email
            password: Password (retrieved from Keychain if None)
            twofa_callback: Function to call when 2FA code is needed

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If login fails
            TwoFactorRequiredError: If 2FA needed but no callback provided
            CredentialsNotFoundError: If no password provided and none stored
        """
        from pyicloud import PyiCloudService
        from pyicloud.exceptions import PyiCloudFailedLoginException

        self._username = username

        # Get password from keychain if not provided
        if password is None:
            password = self.keychain.get_password(
                username, prompt="Authenticate to access iCloud credentials"
            )
            if password is None:
                raise CredentialsNotFoundError(
                    "No stored credentials found. Run 'hide-my-email setup' first."
                )

        # Ensure cookie directory exists
        self.COOKIE_DIR.mkdir(parents=True, exist_ok=True)

        try:
            self._api = PyiCloudService(
                apple_id=username,
                password=password,
                cookie_directory=str(self.COOKIE_DIR),
            )
        except PyiCloudFailedLoginException as e:
            raise AuthenticationError(f"Login failed: {e}") from e

        # Handle 2FA if required
        if self._api.requires_2fa:
            if twofa_callback is None:
                raise TwoFactorRequiredError("2FA required but no callback provided")

            code = twofa_callback()
            if not self._api.validate_2fa_code(code):
                raise AuthenticationError("Invalid 2FA code")

            # Trust this session to reduce future 2FA prompts
            if not self._api.is_trusted_session:
                self._api.trust_session()

        return True

    def is_session_valid(self, username: str) -> bool:
        """
        Check if a valid session exists for the user.

        Args:
            username: Apple ID email

        Returns:
            True if session is valid and doesn't require 2FA
        """
        if not self.keychain.has_password(username):
            return False

        cookie_file = self.COOKIE_DIR / username
        if not cookie_file.exists():
            return False

        try:
            password = self.keychain.get_password(
                username, prompt="Check iCloud session"
            )
            if password:
                from pyicloud import PyiCloudService

                self._api = PyiCloudService(
                    apple_id=username,
                    password=password,
                    cookie_directory=str(self.COOKIE_DIR),
                )
                self._username = username
                return not self._api.requires_2fa
        except Exception:
            pass

        return False

    def clear_session(self, username: str) -> None:
        """
        Clear stored session for a user.

        Args:
            username: Apple ID email
        """
        import shutil

        cookie_path = self.COOKIE_DIR / username
        if cookie_path.exists():
            if cookie_path.is_dir():
                shutil.rmtree(cookie_path)
            else:
                cookie_path.unlink()

        self._api = None
        self._username = None
