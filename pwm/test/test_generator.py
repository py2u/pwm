"""Tests for password generator."""

import pytest
from pwm.utils.generator import (
    generate_password,
    password_strength,
    get_character_pool,
)


class TestPasswordGenerator:
    """Test password generation functionality."""

    def test_default_length(self):
        """Default password should be 20 characters."""
        pw = generate_password()
        assert len(pw) == 20

    def test_custom_length(self):
        """Should generate password of specified length."""
        for length in [4, 8, 16, 32, 64, 128]:
            pw = generate_password(length=length)
            assert len(pw) == length

    def test_contains_all_char_types(self):
        """Default password should contain upper, lower, digit, symbol."""
        pw = generate_password(length=100)
        assert any(c.isupper() for c in pw), "Should contain uppercase"
        assert any(c.islower() for c in pw), "Should contain lowercase"
        assert any(c.isdigit() for c in pw), "Should contain digits"
        assert any(not c.isalnum() for c in pw), "Should contain symbols"

    def test_no_symbols(self):
        """With symbols=False, password should have no symbols."""
        pw = generate_password(length=100, symbols=False)
        assert all(c.isalnum() for c in pw), "Should not contain symbols"

    def test_no_digits(self):
        """With digits=False, password should have no digits."""
        pw = generate_password(length=100, digits=False)
        assert not any(c.isdigit() for c in pw), "Should not contain digits"

    def test_no_upper(self):
        """With upper=False, password should have no uppercase."""
        pw = generate_password(length=100, upper=False)
        assert not any(c.isupper() for c in pw), "Should not contain uppercase"

    def test_no_lower(self):
        """With lower=False, password should have no lowercase."""
        pw = generate_password(length=100, lower=False)
        assert not any(c.islower() for c in pw), "Should not contain lowercase"

    def test_easy_mode_no_ambiguous(self):
        """Easy-mode passwords should not contain ambiguous characters."""
        ambiguous = set("0Oo1lI5S8B")
        for _ in range(50):
            pw = generate_password(length=20, easy_mode=True)
            found = [c for c in pw if c in ambiguous]
            assert len(found) == 0, f"Found ambiguous chars: {found} in '{pw}'"

    def test_easy_mode_has_all_types(self):
        """Easy-mode should still contain all character types."""
        pw = generate_password(length=100, easy_mode=True)
        assert any(c.isupper() for c in pw)
        assert any(c.islower() for c in pw)
        assert any(c.isdigit() for c in pw)
        assert any(not c.isalnum() for c in pw)

    def test_randomness(self):
        """Two generated passwords should be different (probabilistic)."""
        pw1 = generate_password(length=50)
        pw2 = generate_password(length=50)
        assert pw1 != pw2

    def test_minimum_length_with_one_type(self):
        """Length=1 should work when only one character type is enabled."""
        pw = generate_password(length=1, upper=False, lower=True, digits=False, symbols=False)
        assert len(pw) == 1
        assert pw.islower()


class TestPasswordStrength:
    """Test password strength estimation."""

    def test_strong_password(self):
        """A long diverse password should be 'very strong'."""
        pw = generate_password(length=30)
        strength = password_strength(pw)
        assert strength["rating"] == "very strong"
        assert strength["entropy_estimate"] > 100

    def test_weak_password(self):
        """A short simple password should be weak."""
        strength = password_strength("abc123")
        assert strength["rating"] in ("weak", "fair")
        assert strength["entropy_estimate"] < 60

    def test_length_in_output(self):
        """Strength output should include length."""
        strength = password_strength("test123!")
        assert strength["length"] == 8


class TestCharacterPool:
    """Test character pool building."""

    def test_default_pool(self):
        """Default pool should include all character types."""
        pool = get_character_pool()
        assert any(c.isupper() for c in pool)
        assert any(c.islower() for c in pool)
        assert any(c.isdigit() for c in pool)
        assert any(not c.isalnum() for c in pool)

    def test_easy_pool_no_ambiguous(self):
        """Easy pool should not contain ambiguous characters."""
        ambiguous = set("0Oo1lI5S8B")
        pool = get_character_pool(easy_mode=True)
        found = [c for c in pool if c in ambiguous]
        assert len(found) == 0

    def test_restricted_pool(self):
        """Pool with only lowercase and digits."""
        pool = get_character_pool(upper=False, lower=True, digits=True, symbols=False)
        assert not any(c.isupper() for c in pool)
        assert any(c.islower() for c in pool)
        assert any(c.isdigit() for c in pool)
        assert all(c.isalnum() for c in pool)
