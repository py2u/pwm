"""Constants and default values for the PWM password manager."""

import os

# --- Paths ---
VAULT_DIR = os.path.expanduser(os.path.join("~", ".pwm"))
VAULT_FILE = os.path.join(VAULT_DIR, "vault.json")
LOCK_FILE = os.path.join(VAULT_DIR, ".lock")
BACKUP_EXTENSION = ".pwmbackup"

# --- Crypto ---
PBKDF2_ITERATIONS = 600_000       # OWASP 2023 recommendation for SHA256
SALT_LENGTH = 32                  # bytes
KEY_LENGTH = 32                   # bytes (AES-256)
NONCE_LENGTH = 12                 # bytes (GCM standard)

# --- Default config ---
DEFAULT_AUTO_LOCK_TIMEOUT = 300      # seconds (5 minutes)
DEFAULT_CLIPBOARD_CLEAR_TIMEOUT = 30  # seconds
DEFAULT_MAX_FAILED_ATTEMPTS = 5
DEFAULT_LOCKOUT_DURATION = 600       # seconds (10 minutes)

# --- Password generator defaults ---
DEFAULT_PASSWORD_LENGTH = 20

# --- Schema ---
VAULT_VERSION = 1

# --- Display ---
TABLE_COLUMN_WIDTHS = {
    "service": 20,
    "username": 25,
    "password": 16,
    "category": 12,
}
