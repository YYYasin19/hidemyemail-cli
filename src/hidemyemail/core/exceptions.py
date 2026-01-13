"""Custom exceptions for Hide My Email CLI."""


class HideMyEmailError(Exception):
    """Base exception for all Hide My Email errors."""

    pass


class AuthenticationError(HideMyEmailError):
    """Authentication failed."""

    pass


class TwoFactorRequiredError(AuthenticationError):
    """2FA is required but not provided."""

    pass


class SessionExpiredError(AuthenticationError):
    """Session has expired and re-authentication is needed."""

    pass


class CredentialsNotFoundError(AuthenticationError):
    """No stored credentials found."""

    pass


class KeychainError(HideMyEmailError):
    """Keychain operation failed."""

    pass


class TouchIDError(HideMyEmailError):
    """Touch ID authentication failed."""

    pass


class NetworkError(HideMyEmailError):
    """Network request failed."""

    pass


class AliasNotFoundError(HideMyEmailError):
    """Requested alias does not exist."""

    pass


class AliasOperationError(HideMyEmailError):
    """Failed to perform operation on alias."""

    pass
