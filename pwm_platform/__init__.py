"""Platform abstraction layer for PWM.

Automatically selects the appropriate platform implementation at import time.
"""

import sys

from pwm_platform.base import PlatformBase


def _detect_platform() -> str:
    """Detect the current runtime platform."""
    # Check for Android first (Kivy sets this)
    try:
        from jnius import autoclass  # noqa: F401
        return "android"
    except ImportError:
        pass

    # Check for iOS
    try:
        import objc  # noqa: F401
        return "ios"
    except ImportError:
        pass

    # Desktop platforms
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"


_PLATFORM = _detect_platform()

if _PLATFORM == "android":
    from pwm_platform.android import AndroidPlatform as Platform  # noqa: F401
elif _PLATFORM == "ios":
    from pwm_platform.desktop import DesktopPlatform as Platform  # noqa: F401
else:
    from pwm_platform.desktop import DesktopPlatform as Platform  # noqa: F401

__all__ = ["Platform", "_PLATFORM"]
