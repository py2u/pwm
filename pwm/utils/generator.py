"""Secure random password generation."""

import secrets
import math

from pwm.core.constants import DEFAULT_PASSWORD_LENGTH

# Character sets
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_DIGITS = "0123456789"
_SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

# Easy-mode sets (no ambiguous characters: 0/O/o, 1/l/I, 5/S, 8/B)
_UPPER_EASY = "ACDEFGHJKMNPQRTUVWXYZ"     # removed O, I, B, S
_LOWER_EASY = "abcdefghjkmnpqrstuvwxyz"    # removed o, l
_DIGITS_EASY = "234679"                    # removed 0, 1, 5, 8
_SYMBOLS_EASY = "!@#$%^&*()_+-=[]{}|;:,.<>?"


def get_character_pool(
    upper: bool = True,
    lower: bool = True,
    digits: bool = True,
    symbols: bool = True,
    easy_mode: bool = False,
) -> str:
    """Build the character pool based on requested character types."""
    pool = ""
    if upper:
        pool += _UPPER_EASY if easy_mode else _UPPER
    if lower:
        pool += _LOWER_EASY if easy_mode else _LOWER
    if digits:
        pool += _DIGITS_EASY if easy_mode else _DIGITS
    if symbols:
        pool += _SYMBOLS_EASY if easy_mode else _SYMBOLS

    if not pool:
        # If everything is disabled, default to lowercase letters
        pool += _LOWER_EASY if easy_mode else _LOWER
    return pool


def _get_one_from_set(chars: str) -> str:
    """Pick one random character from a set, or empty string if set is empty."""
    return secrets.choice(chars) if chars else ""


def generate_password(
    length: int = DEFAULT_PASSWORD_LENGTH,
    upper: bool = True,
    lower: bool = True,
    digits: bool = True,
    symbols: bool = True,
    easy_mode: bool = False,
) -> str:
    """Generate a cryptographically random password.

    Args:
        length: Desired password length (minimum 4 if all char types enabled).
        upper: Include uppercase letters.
        lower: Include lowercase letters.
        digits: Include digits.
        symbols: Include symbols.
        easy_mode: Exclude ambiguous characters (O/0, l/1, etc.).

    Returns:
        A random password string.
    """
    if length < 1:
        length = DEFAULT_PASSWORD_LENGTH

    # Character sets
    upper_set = _UPPER_EASY if easy_mode else _UPPER
    lower_set = _LOWER_EASY if easy_mode else _LOWER
    digits_set = _DIGITS_EASY if easy_mode else _DIGITS
    symbols_set = _SYMBOLS_EASY if easy_mode else _SYMBOLS

    # Guarantee at least one char from each enabled set
    chars: list[str] = []
    if upper:
        chars.append(secrets.choice(upper_set))
    if lower:
        chars.append(secrets.choice(lower_set))
    if digits:
        chars.append(secrets.choice(digits_set))
    if symbols:
        chars.append(secrets.choice(symbols_set))

    # Fill the rest randomly from the full pool
    pool = get_character_pool(upper, lower, digits, symbols, easy_mode)
    remaining = length - len(chars)
    for _ in range(max(0, remaining)):
        chars.append(secrets.choice(pool))

    # Shuffle to avoid predictable positions (guaranteed chars at the start)
    _secure_shuffle(chars)

    return "".join(chars)


def _secure_shuffle(items: list) -> None:
    """Fisher-Yates shuffle using secrets.SystemRandom for cryptographic randomness."""
    rng = secrets.SystemRandom()
    for i in range(len(items) - 1, 0, -1):
        j = rng.randint(0, i)
        items[i], items[j] = items[j], items[i]


def password_strength(password: str) -> dict:
    """Estimate password strength and return metrics.

    Returns a dict with:
        length: password length
        entropy_estimate: estimated bits of entropy
        char_types: number of character types used
        rating: 'weak', 'fair', 'good', 'strong', 'very strong'
    """
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    char_types = sum([has_upper, has_lower, has_digit, has_symbol])

    # Rough pool size estimate
    pool_size = 0
    if has_upper:
        pool_size += 26
    if has_lower:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if has_symbol:
        pool_size += 20  # conservative estimate

    if pool_size == 0:
        pool_size = 26

    # Entropy = log2(pool_size^length) = length * log2(pool_size)
    entropy = length * math.log2(pool_size)

    if entropy < 40:
        rating = "weak"
    elif entropy < 60:
        rating = "fair"
    elif entropy < 80:
        rating = "good"
    elif entropy < 100:
        rating = "strong"
    else:
        rating = "very strong"

    return {
        "length": length,
        "entropy_estimate": round(entropy, 1),
        "char_types": char_types,
        "rating": rating,
    }
