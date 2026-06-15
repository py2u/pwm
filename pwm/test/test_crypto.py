"""Tests for cryptographic primitives."""

import pytest
from pwm.core.crypto import (
    generate_salt,
    derive_key,
    encrypt,
    decrypt,
    encode_blob,
    decode_blob,
    verify_key,
    secure_erase,
)
from pwm.core.exceptions import WrongPasswordError
from pwm.core.constants import SALT_LENGTH, KEY_LENGTH, NONCE_LENGTH


class TestCrypto:
    """Test cryptographic operations."""

    def test_salt_generation(self):
        """Salt should be cryptographically random and correct length."""
        salt1 = generate_salt()
        salt2 = generate_salt()
        assert len(salt1) == SALT_LENGTH
        assert len(salt2) == SALT_LENGTH
        assert salt1 != salt2  # two salts should be different (probabilistic)

    def test_key_derivation(self):
        """Key derivation should be deterministic and correct length."""
        salt = generate_salt()
        key1 = derive_key("my_password", salt)
        key2 = derive_key("my_password", salt)
        assert len(key1) == KEY_LENGTH
        assert key1 == key2  # same password + same salt = same key

        # Different password = different key
        key3 = derive_key("other_password", salt)
        assert key1 != key3

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypt then decrypt should return original data."""
        key = derive_key("test_password", generate_salt())
        plaintext = b"Hello, World! This is a test message."

        encrypted = encrypt(key, plaintext)
        assert len(encrypted) > len(plaintext)  # has nonce + tag
        assert encrypted != plaintext

        decrypted = decrypt(key, encrypted)
        assert decrypted == plaintext

    def test_encrypt_produces_different_ciphertexts(self):
        """Same plaintext encrypted twice should produce different ciphertexts (random nonce)."""
        key = derive_key("test_password", generate_salt())
        plaintext = b"repeat"

        ct1 = encrypt(key, plaintext)
        ct2 = encrypt(key, plaintext)
        assert ct1 != ct2  # nonce ensures different ciphertexts

    def test_wrong_password_detected(self):
        """Decrypt with wrong key should raise WrongPasswordError."""
        salt = generate_salt()
        key1 = derive_key("correct_password", salt)
        key2 = derive_key("wrong_password", salt)
        encrypted = encrypt(key1, b"secret data")

        with pytest.raises(WrongPasswordError):
            decrypt(key2, encrypted)

    def test_tampered_ciphertext_detected(self):
        """Tampered ciphertext should raise WrongPasswordError."""
        key = derive_key("test_password", generate_salt())
        encrypted = bytearray(encrypt(key, b"secret data"))

        # Tamper with a byte in the ciphertext portion
        encrypted[NONCE_LENGTH + 2] ^= 0xFF

        with pytest.raises(WrongPasswordError):
            decrypt(key, bytes(encrypted))

    def test_verify_key(self):
        """verify_key should return True/False without raising."""
        salt = generate_salt()
        key1 = derive_key("correct", salt)
        key2 = derive_key("wrong", salt)
        encrypted = encrypt(key1, b"test")

        assert verify_key(key1, encrypted) is True
        assert verify_key(key2, encrypted) is False

    def test_base64_roundtrip(self):
        """Base64 encode/decode should be reversible."""
        data = b"\x00\x01\x02\xff\xfe\xfd" * 10
        encoded = encode_blob(data)
        decoded = decode_blob(encoded)
        assert decoded == data

    def test_secure_erase(self):
        """secure_erase should zero out a bytearray."""
        data = bytearray(b"sensitive_key_material_12345")
        secure_erase(data)
        assert data == bytearray(b"\x00" * len(data))

    def test_various_plaintext_sizes(self):
        """Encrypt/decrypt should work for various sizes."""
        key = derive_key("test", generate_salt())
        for size in [0, 1, 16, 64, 256, 1024, 4096]:
            plaintext = b"x" * size
            encrypted = encrypt(key, plaintext)
            decrypted = decrypt(key, encrypted)
            assert decrypted == plaintext, f"Failed for size {size}"
