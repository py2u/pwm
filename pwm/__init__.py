"""PWM — A secure, local CLI password manager with AES-256-GCM encryption.

Subpackages:
    core     — Cryptographic primitives, vault logic, data models, exceptions
    cli      — Command-line interface (argument parsing and command handlers)
    utils    — Password generation and clipboard utilities
    config   — Configuration management (reserved for future expansion)
    test     — Test suite
"""

from pwm._version import __version__, __version_tuple__, get_version, get_version_tuple

# Re-export commonly used names at the package level for convenience
from pwm.core import (
    # Exceptions
    PwmError,
    VaultNotFoundError,
    VaultAlreadyExistsError,
    WrongPasswordError,
    VaultLockedError,
    LockoutError,
    AccountNotFoundError,
    AccountDuplicateError,
    CryptoError,
    ClipboardError,
    ConfigError,
    # Models
    Account,
    VaultConfig,
    VaultFile,
    PlaintextData,
)
from pwm.utils import (
    generate_password,
    password_strength,
    copy_to_clipboard,
    schedule_clipboard_clear,
)

__all__ = [
    "__version__",
    "__version_tuple__",
    "get_version",
    "get_version_tuple",
    # Exceptions
    "PwmError",
    "VaultNotFoundError",
    "VaultAlreadyExistsError",
    "WrongPasswordError",
    "VaultLockedError",
    "LockoutError",
    "AccountNotFoundError",
    "AccountDuplicateError",
    "CryptoError",
    "ClipboardError",
    "ConfigError",
    # Models
    "Account",
    "VaultConfig",
    "VaultFile",
    "PlaintextData",
    # Utils
    "generate_password",
    "password_strength",
    "copy_to_clipboard",
    "schedule_clipboard_clear",
]
