"""Keychain operations using PyObjC Security framework with Touch ID protection."""

from __future__ import annotations

SERVICE_NAME = "com.hidemyemail.cli"

# Common Security framework error codes
# See: https://developer.apple.com/documentation/security/1542001-security_framework_result_codes
SEC_ERROR_MESSAGES = {
    0: "Success",
    -4: "Function or operation not implemented",
    -25291: "No keychain is available",
    -25292: "The specified keychain is not a valid keychain file",
    -25293: "The specified keychain could not be opened",
    -25294: "A duplicate keychain item already exists",
    -25295: "The specified item could not be found in the keychain",
    -25296: "Keychain interaction is not allowed by the caller",
    -25297: "The keychain interaction was blocked by the user",
    -25298: "The caller does not have access to the keychain item",
    -25299: "The specified data is invalid for keychain",
    -25300: "No default keychain exists",
    -25308: "Interaction with the Security Server is not allowed",
    -26275: "An authorization/authentication was canceled",
    -26276: "Authorization/Authentication failed",
    -34018: "A required entitlement is missing (code signing issue)",
    -50: "One or more parameters passed were not valid",
    -67030: "Device passcode is not set (required for biometric protection)",
}


def get_security_error_message(status: int) -> str:
    """Get human-readable error message for Security framework status code."""
    if status in SEC_ERROR_MESSAGES:
        return f"{SEC_ERROR_MESSAGES[status]} (error {status})"
    return f"Unknown security error (error {status})"


class KeychainError(Exception):
    """Keychain operation failed."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class KeychainManager:
    """Manage credentials in macOS Keychain with optional Touch ID protection."""

    def __init__(self) -> None:
        self._security_available = self._check_security_framework()
        self._last_error: str | None = None

    def _check_security_framework(self) -> bool:
        """Check if Security framework is available."""
        try:
            import Security  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def last_error(self) -> str | None:
        """Get the last error message."""
        return self._last_error

    def store_password(
        self, account: str, password: str, require_biometry: bool = True
    ) -> bool:
        """
        Store password in Keychain, optionally protected by Touch ID.

        Note: Due to macOS entitlement requirements, Python scripts cannot create
        keychain items with biometric protection directly. We use the `security`
        CLI tool instead and handle Touch ID authentication separately.

        Args:
            account: The account identifier (e.g., Apple ID email)
            password: The password to store
            require_biometry: If True, Touch ID will be required to retrieve
                             (enforced at retrieval time, not storage time)

        Returns:
            True if successful
        """
        self._last_error = None

        # Always use the security CLI tool for storage
        # PyObjC approach fails with -34018 (missing entitlements) for biometry
        return self._store_password_fallback(account, password)

    def get_password(
        self, account: str, prompt: str = "Authenticate to access credentials"
    ) -> str | None:
        """
        Retrieve password from Keychain with Touch ID authentication.

        Args:
            account: The account identifier
            prompt: Message shown during Touch ID authentication

        Returns:
            The password if found and authenticated, None otherwise
        """
        self._last_error = None

        # First, authenticate with Touch ID if available
        from hidemyemail.auth.touchid import authenticate, is_available

        if is_available():
            success, error = authenticate(prompt)
            if not success:
                self._last_error = f"Touch ID authentication failed: {error}"
                return None

        # Then retrieve from keychain using security CLI
        return self._get_password_fallback(account)

    def delete_password(self, account: str) -> bool:
        """
        Delete password from Keychain.

        Args:
            account: The account identifier

        Returns:
            True if deleted or didn't exist
        """
        return self._delete_password_fallback(account)

    def has_password(self, account: str) -> bool:
        """
        Check if a password exists for the account (without triggering Touch ID).

        Args:
            account: The account identifier

        Returns:
            True if password exists
        """
        return self._has_password_fallback(account)

    # Methods using subprocess + security command
    def _store_password_fallback(self, account: str, password: str) -> bool:
        """Store password using security command."""
        import subprocess

        try:
            # Delete existing first (ignore errors if it doesn't exist)
            subprocess.run(
                [
                    "/usr/bin/security",
                    "delete-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    account,
                ],
                capture_output=True,
            )

            # Add new password
            result = subprocess.run(
                [
                    "/usr/bin/security",
                    "add-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    account,
                    "-w",
                    password,
                    "-U",  # Update if exists
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()
                if stderr:
                    self._last_error = f"security command failed: {stderr}"
                else:
                    self._last_error = f"security command failed with code {result.returncode}"
                return False

            return True

        except FileNotFoundError:
            self._last_error = "/usr/bin/security command not found"
            return False
        except Exception as e:
            self._last_error = f"Unexpected error: {e}"
            return False

    def _get_password_fallback(self, account: str) -> str | None:
        """Get password using security command."""
        import subprocess

        try:
            result = subprocess.run(
                [
                    "/usr/bin/security",
                    "find-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    account,
                    "-w",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout.strip()

            # Item not found is not an error we need to report
            if "could not be found" in result.stderr:
                self._last_error = "No credentials found for this account"
            else:
                self._last_error = result.stderr.strip() or f"Failed with code {result.returncode}"

            return None

        except FileNotFoundError:
            self._last_error = "/usr/bin/security command not found"
            return None
        except Exception as e:
            self._last_error = f"Unexpected error: {e}"
            return None

    def _delete_password_fallback(self, account: str) -> bool:
        """Delete password using security command."""
        import subprocess

        try:
            result = subprocess.run(
                [
                    "/usr/bin/security",
                    "delete-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    account,
                ],
                capture_output=True,
                text=True,
            )
            # Return True even if item wasn't found (already deleted)
            return result.returncode == 0 or "could not be found" in result.stderr

        except Exception as e:
            self._last_error = f"Unexpected error: {e}"
            return False

    def _has_password_fallback(self, account: str) -> bool:
        """Check if password exists using security command."""
        import subprocess

        try:
            result = subprocess.run(
                [
                    "/usr/bin/security",
                    "find-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    account,
                ],
                capture_output=True,
            )
            return result.returncode == 0

        except Exception:
            return False
