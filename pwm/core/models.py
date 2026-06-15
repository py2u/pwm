"""Data models for the PWM password manager."""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

from pwm.core.constants import VAULT_VERSION, DEFAULT_AUTO_LOCK_TIMEOUT, DEFAULT_CLIPBOARD_CLEAR_TIMEOUT, \
    DEFAULT_MAX_FAILED_ATTEMPTS, DEFAULT_LOCKOUT_DURATION


@dataclass
class Account:
    """A single stored account credential."""
    service: str
    username: str
    password: str
    notes: str = ""
    category: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Account":
        return cls(**d)


@dataclass
class VaultConfig:
    """User-configurable vault settings."""
    auto_lock_timeout: int = DEFAULT_AUTO_LOCK_TIMEOUT
    clipboard_clear_timeout: int = DEFAULT_CLIPBOARD_CLEAR_TIMEOUT
    max_failed_attempts: int = DEFAULT_MAX_FAILED_ATTEMPTS
    lockout_duration: int = DEFAULT_LOCKOUT_DURATION

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "VaultConfig":
        # Only take keys that exist in the dataclass
        valid_keys = {"auto_lock_timeout", "clipboard_clear_timeout", "max_failed_attempts", "lockout_duration"}
        filtered = {k: v for k, v in d.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class VaultFile:
    """Represents the on-disk encrypted vault structure (metadata + encrypted payload)."""
    version: int
    salt: str                     # base64-encoded
    encrypted_data: str           # base64-encoded (nonce + ciphertext+tag)
    failed_attempts: int = 0
    lockout_until: Optional[float] = None
    last_activity: float = 0.0
    config: VaultConfig = field(default_factory=VaultConfig)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["config"] = self.config.to_dict()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "VaultFile":
        config_data = d.pop("config", {})
        config = VaultConfig.from_dict(config_data)
        return cls(
            version=d.get("version", VAULT_VERSION),
            salt=d.get("salt", ""),
            encrypted_data=d.get("encrypted_data", ""),
            failed_attempts=d.get("failed_attempts", 0),
            lockout_until=d.get("lockout_until"),
            last_activity=d.get("last_activity", 0.0),
            config=config,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "VaultFile":
        return cls.from_dict(json.loads(json_str))


@dataclass
class PlaintextData:
    """The decrypted payload inside encrypted_data — the actual accounts."""
    accounts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"accounts": [a.to_dict() for a in self.accounts]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "PlaintextData":
        accounts = [Account.from_dict(a) for a in d.get("accounts", [])]
        return cls(accounts=accounts)

    @classmethod
    def from_json(cls, json_str: str) -> "PlaintextData":
        return cls.from_dict(json.loads(json_str))
