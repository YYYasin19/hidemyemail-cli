"""Touch ID authentication using PyObjC LocalAuthentication framework."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Load libdispatch for synchronous waiting
_libdispatch = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
_libdispatch.dispatch_semaphore_create.restype = ctypes.c_void_p
_libdispatch.dispatch_semaphore_create.argtypes = [ctypes.c_long]
_libdispatch.dispatch_semaphore_wait.restype = ctypes.c_long
_libdispatch.dispatch_semaphore_wait.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
_libdispatch.dispatch_semaphore_signal.restype = ctypes.c_long
_libdispatch.dispatch_semaphore_signal.argtypes = [ctypes.c_void_p]

_DISPATCH_TIME_FOREVER = 0xFFFFFFFFFFFFFFFF


def is_available() -> bool:
    """Check if Touch ID is available on this device."""
    try:
        from LocalAuthentication import (
            LAContext,
            LAPolicyDeviceOwnerAuthenticationWithBiometrics,
        )

        context = LAContext.alloc().init()
        can_evaluate, _ = context.canEvaluatePolicy_error_(
            LAPolicyDeviceOwnerAuthenticationWithBiometrics, None
        )
        return bool(can_evaluate)
    except ImportError:
        return False
    except Exception:
        return False


def authenticate(reason: str = "Access Hide My Email credentials") -> tuple[bool, str | None]:
    """
    Authenticate user via Touch ID.

    Args:
        reason: The message shown to the user during authentication.

    Returns:
        Tuple of (success: bool, error_message: str | None)
    """
    try:
        from LocalAuthentication import (
            LAContext,
            LAPolicyDeviceOwnerAuthenticationWithBiometrics,
        )
    except ImportError:
        return False, "LocalAuthentication framework not available"

    context = LAContext.alloc().init()

    can_evaluate, error = context.canEvaluatePolicy_error_(
        LAPolicyDeviceOwnerAuthenticationWithBiometrics, None
    )

    if not can_evaluate:
        error_msg = error.localizedDescription() if error else "Touch ID not available"
        return False, str(error_msg)

    # Create semaphore for synchronous wait
    semaphore = _libdispatch.dispatch_semaphore_create(0)

    result: dict[str, bool | str | None] = {"success": False, "error": None}

    def callback(success: bool, auth_error: object) -> None:
        result["success"] = success
        if auth_error:
            result["error"] = str(auth_error.localizedDescription())
        _libdispatch.dispatch_semaphore_signal(semaphore)

    context.evaluatePolicy_localizedReason_reply_(
        LAPolicyDeviceOwnerAuthenticationWithBiometrics,
        reason,
        callback,
    )

    _libdispatch.dispatch_semaphore_wait(semaphore, _DISPATCH_TIME_FOREVER)

    return bool(result["success"]), result["error"]  # type: ignore[return-value]
