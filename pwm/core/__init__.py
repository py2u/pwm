"""Core package for PWM — cryptographic primitives, vault logic, and data models."""

from pwm.core.constants import (
    VAULT_DIR,
    VAULT_FILE,
    VAULT_VERSION,
    DEFAULT_PASSWORD_LENGTH,
    DEFAULT_AUTO_LOCK_TIMEOUT,
    DEFAULT_CLIPBOARD_CLEAR_TIMEOUT,
    DEFAULT_MAX_FAILED_ATTEMPTS,
    DEFAULT_LOCKOUT_DURATION,
)
from pwm.core.exceptions import (
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
)
from pwm.core.models import (
    Account,
    VaultConfig,
    VaultFile,
    PlaintextData,
)
from pwm.core.crypto import (
    generate_salt,
    derive_key,
    encrypt,
    decrypt,
    encode_blob,
    decode_blob,
    secure_erase,
    verify_key,
)

__all__ = [
    # constants
    "VAULT_DIR", "VAULT_FILE", "VAULT_VERSION",
    "DEFAULT_PASSWORD_LENGTH", "DEFAULT_AUTO_LOCK_TIMEOUT",
    "DEFAULT_CLIPBOARD_CLEAR_TIMEOUT", "DEFAULT_MAX_FAILED_ATTEMPTS",
    "DEFAULT_LOCKOUT_DURATION",
    # exceptions
    "PwmError", "VaultNotFoundError", "VaultAlreadyExistsError",
    "WrongPasswordError", "VaultLockedError", "LockoutError",
    "AccountNotFoundError", "AccountDuplicateError", "CryptoError",
    "ClipboardError", "ConfigError",
    # models
    "Account", "VaultConfig", "VaultFile", "PlaintextData",
    # crypto
    "generate_salt", "derive_key", "encrypt", "decrypt",
    "encode_blob", "decode_blob", "secure_erase", "verify_key",
]
