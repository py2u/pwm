"""Custom exception hierarchy for PWM password manager."""


class PwmError(Exception):
    """Base exception for all PWM errors."""
    pass


class VaultNotFoundError(PwmError):
    """Vault file does not exist."""

    def __init__(self, path: str = ""):
        self.path = path
        super().__init__(f"Vault not found: {path}" if path else "Vault not found. Run 'pwm init' first.")


class VaultAlreadyExistsError(PwmError):
    """Tried to initialize when vault already exists."""

    def __init__(self, path: str = ""):
        self.path = path
        super().__init__(
            f"Vault already exists at: {path}" if path else "Vault already exists. Use your existing vault."
        )


class WrongPasswordError(PwmError):
    """Master password is incorrect."""

    def __init__(self, remaining: int = 0):
        self.remaining = remaining
        msg = "Incorrect master password."
        if remaining > 0:
            msg += f" {remaining} attempt(s) remaining before lockout."
        super().__init__(msg)


class VaultLockedError(PwmError):
    """Vault is locked (auto-lock or manual lock)."""

    def __init__(self):
        super().__init__("Vault is locked. Please enter your master password to unlock.")


class LockoutError(PwmError):
    """Too many failed attempts — vault is temporarily locked."""

    def __init__(self, until_timestamp: float):
        import datetime
        dt = datetime.datetime.fromtimestamp(until_timestamp)
        self.until = until_timestamp
        super().__init__(
            f"Too many failed attempts. Vault locked until {dt.strftime('%Y-%m-%d %H:%M:%S')}."
        )


class AccountNotFoundError(PwmError):
    """Account lookup by service name failed."""

    def __init__(self, service: str):
        self.service = service
        super().__init__(f"No account found for: {service}")


class AccountDuplicateError(PwmError):
    """Tried to add an account with a service name that already exists."""

    def __init__(self, service: str):
        self.service = service
        super().__init__(f"An account for '{service}' already exists. Use 'pwm edit {service}' to update it.")


class CryptoError(PwmError):
    """Wraps cryptography-level errors."""

    def __init__(self, message: str = "A cryptographic error occurred."):
        super().__init__(message)


class ClipboardError(PwmError):
    """Clipboard tool is unavailable on this system."""

    def __init__(self):
        super().__init__(
            "No clipboard tool found. On Windows, 'clip.exe' should be available. "
            "On Linux, install 'xclip' or 'wl-clipboard'."
        )


class ConfigError(PwmError):
    """Invalid configuration key or value."""

    def __init__(self, message: str):
        super().__init__(message)
