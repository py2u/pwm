"""Version information for PWM.

Uses a simple major.minor.patch scheme.
"""

__version__ = "1.0.0"
__version_tuple__ = (1, 0, 0)

def get_version() -> str:
    """Return the current version string."""
    return __version__

def get_version_tuple() -> tuple:
    """Return the current version as a tuple."""
    return __version_tuple__
