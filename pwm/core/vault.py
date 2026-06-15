"""Vault lifecycle management for the PWM password manager.

Maintains an in-memory session with the decrypted key material and account data.
All persistent mutations go through save() which re-encrypts and writes to disk.
"""

import os
import time

from pwm.core.constants import (
    VAULT_DIR,
    VAULT_FILE,
    VAULT_VERSION,
)
from pwm.core.crypto import (
    generate_salt,
    derive_key,
    encrypt,
    decrypt,
    encode_blob,
    decode_blob,
    secure_erase,
)
from pwm.core.models import (
    Account,
    VaultConfig,
    VaultFile,
    PlaintextData,
)
from pwm.core.exceptions import (
    VaultNotFoundError,
    VaultAlreadyExistsError,
    WrongPasswordError,
    VaultLockedError,
    LockoutError,
    AccountNotFoundError,
    AccountDuplicateError,
    CryptoError,
    ConfigError,
)


# ---------------------------------------------------------------------------
# In-memory session state (module-level)
# ---------------------------------------------------------------------------

_session: dict = {
    "key": None,              # bytes | None — the derived AES-256 key
    "vault_file": None,       # VaultFile | None — vault metadata
    "plaintext_data": None,   # PlaintextData | None — decrypted accounts
    "last_activity": None,    # float | None — timestamp of last action
    "vault_path": None,       # str | None — path to the vault file
}


def _reset_session() -> None:
    """Clear all in-memory session state and zero the key."""
    key = _session.get("key")
    if key is not None:
        secure_erase(bytearray(key))
    _session["key"] = None
    _session["vault_file"] = None
    _session["plaintext_data"] = None
    _session["last_activity"] = None
    _session["vault_path"] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dir(path: str) -> None:
    """Create the vault directory if it doesn't exist, with 0o700 permissions."""
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    # Best-effort: restrict directory permissions
    try:
        os.chmod(dir_path, 0o700)
    except (OSError, PermissionError):
        pass


def _read_vault_file(path: str) -> VaultFile:
    """Read and parse the vault file from disk."""
    if not os.path.exists(path):
        raise VaultNotFoundError(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return VaultFile.from_json(f.read())
    except VaultNotFoundError:
        raise
    except Exception as e:
        raise CryptoError(f"Failed to read vault file: {e}") from e


def _write_vault_file(vault_file: VaultFile, path: str) -> None:
    """Write the vault file to disk atomically (write-to-temp + rename)."""
    _ensure_dir(path)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(vault_file.to_json())
        os.replace(tmp_path, path)
        # Best-effort: restrict file permissions
        try:
            os.chmod(path, 0o600)
        except (OSError, PermissionError):
            pass
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise CryptoError(f"Failed to write vault file: {e}") from e


def _resolve_path(path: str | None = None) -> str:
    """Resolve vault path: explicit argument > session > default."""
    if path:
        return path
    if _session.get("vault_path"):
        return _session["vault_path"]
    return VAULT_FILE


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_vault(master_password: str, vault_path: str | None = None) -> str:
    """Initialize a new vault with the given master password.

    Returns the path to the created vault file.
    """
    path = _resolve_path(vault_path)
    if os.path.exists(path):
        raise VaultAlreadyExistsError(path)

    salt = generate_salt()
    key = derive_key(master_password, salt)

    plaintext_data = PlaintextData(accounts=[])
    encrypted_blob = encrypt(key, plaintext_data.to_json().encode("utf-8"))

    vault_file = VaultFile(
        version=VAULT_VERSION,
        salt=encode_blob(salt),
        encrypted_data=encode_blob(encrypted_blob),
        last_activity=time.time(),
    )

    _write_vault_file(vault_file, path)

    # Populate session so the vault is ready to use immediately
    _session["key"] = key
    _session["vault_file"] = vault_file
    _session["plaintext_data"] = plaintext_data
    _session["last_activity"] = time.time()
    _session["vault_path"] = path

    return path


def unlock_vault(master_password: str, vault_path: str | None = None) -> None:
    """Unlock an existing vault with the master password.

    Raises:
        VaultNotFoundError: no vault file exists
        LockoutError: vault is currently locked out
        WrongPasswordError: password is incorrect
    """
    global _session
    path = _resolve_path(vault_path)
    vault_file = _read_vault_file(path)

    # Check lockout before doing expensive key derivation
    if vault_file.lockout_until is not None and time.time() < vault_file.lockout_until:
        raise LockoutError(vault_file.lockout_until)

    # If lockout has expired, clear it
    if vault_file.lockout_until is not None and time.time() >= vault_file.lockout_until:
        vault_file.lockout_until = None
        vault_file.failed_attempts = 0

    salt = decode_blob(vault_file.salt)
    key = derive_key(master_password, salt)

    try:
        encrypted_blob = decode_blob(vault_file.encrypted_data)
        plaintext_bytes = decrypt(key, encrypted_blob)
        plaintext_data = PlaintextData.from_json(plaintext_bytes.decode("utf-8"))
    except WrongPasswordError:
        # Increment failed attempts
        vault_file.failed_attempts += 1
        cfg = vault_file.config

        if vault_file.failed_attempts >= cfg.max_failed_attempts:
            vault_file.lockout_until = time.time() + cfg.lockout_duration
            _write_vault_file(vault_file, path)
            raise LockoutError(vault_file.lockout_until)

        _write_vault_file(vault_file, path)
        remaining = cfg.max_failed_attempts - vault_file.failed_attempts
        raise WrongPasswordError(remaining)

    # Success — reset failure counters
    vault_file.failed_attempts = 0
    vault_file.lockout_until = None
    vault_file.last_activity = time.time()

    # Populate session
    _session["key"] = key
    _session["vault_file"] = vault_file
    _session["plaintext_data"] = plaintext_data
    _session["last_activity"] = time.time()
    _session["vault_path"] = path


def lock_vault() -> None:
    """Lock the vault: save state to disk and clear in-memory session."""
    path = _session.get("vault_path")
    if path and _session["plaintext_data"] is not None and _session["key"] is not None:
        _save()
    _reset_session()


def _save() -> None:
    """Re-encrypt plaintext data and write to disk."""
    path = _session.get("vault_path")
    key = _session.get("key")
    plaintext_data = _session.get("plaintext_data")
    vault_file = _session.get("vault_file")

    if not all([path, key, plaintext_data, vault_file]):
        raise CryptoError("Cannot save: session is not fully initialized.")

    # Re-encrypt with a fresh nonce
    encrypted_blob = encrypt(key, plaintext_data.to_json().encode("utf-8"))
    vault_file.encrypted_data = encode_blob(encrypted_blob)
    vault_file.last_activity = _session["last_activity"] or time.time()
    vault_file.version = VAULT_VERSION

    _write_vault_file(vault_file, path)


def _check_auto_lock() -> None:
    """Check if the auto-lock timeout has been exceeded. Locks vault if so."""
    vault_file = _session.get("vault_file")
    last = _session.get("last_activity")

    if vault_file is None or last is None:
        raise VaultLockedError()

    timeout = vault_file.config.auto_lock_timeout
    if timeout > 0 and (time.time() - last) > timeout:
        lock_vault()
        raise VaultLockedError()


def ensure_unlocked() -> None:
    """Guard: raise VaultLockedError if session is not active, or auto-locked.

    Call this at the start of every command that requires an unlocked vault.
    """
    if _session["key"] is None or _session["plaintext_data"] is None:
        # Try to auto-unlock by checking if we have a vault_path
        # (Actual unlock requires re-prompting, which happens in CLI layer)
        raise VaultLockedError()
    _check_auto_lock()


def touch_activity() -> None:
    """Update the last-activity timestamp after a successful command."""
    _session["last_activity"] = time.time()
    vf = _session.get("vault_file")
    if vf:
        vf.last_activity = time.time()


def is_unlocked() -> bool:
    """Return True if the vault is currently unlocked."""
    try:
        ensure_unlocked()
        return True
    except VaultLockedError:
        return False


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------

def get_accounts() -> list[Account]:
    """Return all accounts (requires unlocked vault)."""
    ensure_unlocked()
    return list(_session["plaintext_data"].accounts)


def find_account(service: str) -> Account:
    """Find an account by service name (case-insensitive).

    Raises AccountNotFoundError if not found.
    """
    ensure_unlocked()
    accounts = _session["plaintext_data"].accounts
    for acc in accounts:
        if acc.service.lower() == service.lower():
            return acc
    raise AccountNotFoundError(service)


def add_account(account: Account) -> None:
    """Add a new account. Raises AccountDuplicateError if service already exists."""
    ensure_unlocked()
    accounts = _session["plaintext_data"].accounts

    # Check for duplicate (case-insensitive)
    for acc in accounts:
        if acc.service.lower() == account.service.lower():
            raise AccountDuplicateError(account.service)

    account.created_at = time.time()
    account.updated_at = time.time()
    accounts.append(account)
    _session["last_activity"] = time.time()
    _save()


def update_account(service: str, updates: dict) -> Account:
    """Update fields on an existing account.

    The 'updates' dict may contain: service, username, password, notes, category.
    Returns the updated Account.
    """
    ensure_unlocked()
    acc = find_account(service)

    for field in ("service", "username", "password", "notes", "category"):
        if field in updates and updates[field] is not None:
            setattr(acc, field, updates[field])

    acc.updated_at = time.time()
    _session["last_activity"] = time.time()
    _save()
    return acc


def delete_account(service: str) -> None:
    """Delete an account by service name.

    Raises AccountNotFoundError if not found.
    """
    ensure_unlocked()
    accounts = _session["plaintext_data"].accounts
    for i, acc in enumerate(accounts):
        if acc.service.lower() == service.lower():
            accounts.pop(i)
            _session["last_activity"] = time.time()
            _save()
            return
    raise AccountNotFoundError(service)


def search_accounts(query: str, category_only: bool = False) -> list[Account]:
    """Search accounts by service name and/or category (case-insensitive substring match)."""
    ensure_unlocked()
    accounts = _session["plaintext_data"].accounts
    q = query.lower()
    results = []
    for acc in accounts:
        if category_only:
            if q in acc.category.lower():
                results.append(acc)
        else:
            if q in acc.service.lower() or q in acc.category.lower():
                results.append(acc)
    return results


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------

def export_vault(export_path: str, vault_path: str | None = None) -> str:
    """Export the encrypted vault file to the given path.

    No decryption is performed — the export stays encrypted.
    Returns the absolute path of the export file.
    """
    path = _resolve_path(vault_path)
    if not os.path.exists(path):
        raise VaultNotFoundError(path)

    export_path = os.path.abspath(export_path)
    with open(path, "rb") as src:
        with open(export_path, "wb") as dst:
            dst.write(src.read())
    return export_path


def import_vault(import_path: str, mode: str = "merge") -> int:
    """Import accounts from an exported vault file.

    Args:
        import_path: Path to the exported vault file.
        mode: 'merge' (default) — add imported accounts, skip duplicates.
              'replace' — replace all current accounts with imported ones.

    Returns the number of imported accounts.

    The vault must be unlocked. The imported vault must use the same master
    password (i.e., be decryptable with the current session key).
    """
    ensure_unlocked()

    if not os.path.exists(import_path):
        raise VaultNotFoundError(import_path)

    # Read the import file as a VaultFile
    try:
        with open(import_path, "r", encoding="utf-8") as f:
            imported_vault = VaultFile.from_json(f.read())
    except Exception as e:
        raise CryptoError(f"Failed to read import file: {e}") from e

    # Decrypt with current session key (validates same master password)
    current_key = _session["key"]
    try:
        encrypted_blob = decode_blob(imported_vault.encrypted_data)
        plaintext_bytes = decrypt(current_key, encrypted_blob)
        imported_data = PlaintextData.from_json(plaintext_bytes.decode("utf-8"))
    except WrongPasswordError:
        raise WrongPasswordError(0)  # generic message — the import was encrypted with a different key
    except Exception as e:
        raise CryptoError(f"Failed to decrypt import: {e}") from e

    current_accounts = _session["plaintext_data"].accounts
    current_services = {a.service.lower() for a in current_accounts}
    imported_count = 0

    if mode == "replace":
        current_accounts.clear()
        for acc in imported_data.accounts:
            current_accounts.append(acc)
            imported_count += 1
    else:  # merge
        for acc in imported_data.accounts:
            if acc.service.lower() not in current_services:
                current_accounts.append(acc)
                current_services.add(acc.service.lower())
                imported_count += 1

    _session["last_activity"] = time.time()
    _save()
    return imported_count


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def get_config() -> VaultConfig:
    """Return the current vault configuration."""
    ensure_unlocked()
    return _session["vault_file"].config


def set_config(updates: dict) -> VaultConfig:
    """Update vault configuration settings.

    Valid keys: auto_lock_timeout, clipboard_clear_timeout, max_failed_attempts, lockout_duration.
    """
    ensure_unlocked()
    config = _session["vault_file"].config
    valid_keys = {"auto_lock_timeout", "clipboard_clear_timeout", "max_failed_attempts", "lockout_duration"}

    for key, value in updates.items():
        if key not in valid_keys:
            raise ConfigError(f"Unknown config key: {key}. Valid keys: {', '.join(sorted(valid_keys))}")
        if not isinstance(value, int) or value < 0:
            raise ConfigError(f"Value for '{key}' must be a non-negative integer, got: {value}")
        setattr(config, key, value)

    _session["last_activity"] = time.time()
    _save()
    return config


# ---------------------------------------------------------------------------
# Change master password
# ---------------------------------------------------------------------------

def change_master_password(new_password: str) -> None:
    """Change the master password: re-salt, re-derive, re-encrypt."""
    ensure_unlocked()

    new_salt = generate_salt()
    new_key = derive_key(new_password, new_salt)

    plaintext_data = _session["plaintext_data"]
    encrypted_blob = encrypt(new_key, plaintext_data.to_json().encode("utf-8"))

    vault_file = _session["vault_file"]
    vault_file.salt = encode_blob(new_salt)
    vault_file.encrypted_data = encode_blob(encrypted_blob)
    vault_file.last_activity = time.time()

    # Replace key in session
    old_key = _session["key"]
    if old_key is not None:
        secure_erase(bytearray(old_key))
    _session["key"] = new_key
    _session["last_activity"] = time.time()

    _write_vault_file(vault_file, _session["vault_path"])
