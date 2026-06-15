"""Cryptographic primitives for the PWM password manager.

Uses AES-256-GCM for authenticated encryption and PBKDF2-SHA256 for key derivation.
Depends on the 'cryptography' library.
"""

import base64
import os
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from pwm.core.constants import (
    SALT_LENGTH,
    KEY_LENGTH,
    NONCE_LENGTH,
    PBKDF2_ITERATIONS,
)
from pwm.core.exceptions import WrongPasswordError, CryptoError


def generate_salt() -> bytes:
    """Generate a cryptographically random salt for PBKDF2."""
    return secrets.token_bytes(SALT_LENGTH)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from a master password and salt using PBKDF2-SHA256.

    Uses 600,000 iterations as per OWASP 2023 recommendations.
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return kdf.derive(password.encode("utf-8"))
    except Exception as e:
        raise CryptoError(f"Key derivation failed: {e}") from e


def encrypt(key: bytes, plaintext: bytes) -> bytes:
    """Encrypt plaintext using AES-256-GCM with a fresh random nonce.

    Returns: nonce (12 bytes) + ciphertext_with_tag
    The GCM authentication tag is included at the end of the ciphertext by AESGCM.
    """
    try:
        nonce = os.urandom(NONCE_LENGTH)
        aesgcm = AESGCM(key)
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext_with_tag
    except Exception as e:
        raise CryptoError(f"Encryption failed: {e}") from e


def decrypt(key: bytes, encrypted_blob: bytes) -> bytes:
    """Decrypt data encrypted with encrypt().

    Expects: nonce (12 bytes) + ciphertext_with_tag
    Raises WrongPasswordError if authentication fails (wrong key or tampered data).
    """
    try:
        if len(encrypted_blob) < NONCE_LENGTH + 16:
            raise WrongPasswordError()
        nonce = encrypted_blob[:NONCE_LENGTH]
        ciphertext_with_tag = encrypted_blob[NONCE_LENGTH:]
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        return plaintext
    except InvalidTag:
        raise WrongPasswordError()
    except WrongPasswordError:
        raise
    except Exception as e:
        raise CryptoError(f"Decryption failed: {e}") from e


def verify_key(key: bytes, encrypted_blob: bytes) -> bool:
    """Check whether a key can decrypt an encrypted blob. Returns True/False."""
    try:
        decrypt(key, encrypted_blob)
        return True
    except (WrongPasswordError, CryptoError):
        return False


def encode_blob(blob: bytes) -> str:
    """Base64-encode binary data for JSON storage."""
    return base64.b64encode(blob).decode("ascii")


def decode_blob(encoded: str) -> bytes:
    """Base64-decode a string back to binary data."""
    return base64.b64decode(encoded)


def secure_erase(data: bytearray) -> None:
    """Overwrite a bytearray with zeros in-place.

    This reduces the window where sensitive data sits in memory.
    Note: Python strings are immutable so the caller should avoid holding
    plaintext passwords in str form longer than necessary.
    """
    for i in range(len(data)):
        data[i] = 0
