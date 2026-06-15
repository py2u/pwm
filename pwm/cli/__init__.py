"""CLI package for PWM — argument parsing and command handlers."""

from pwm.cli.commands import (
    build_parser,
    ensure_vault_unlocked,
    prompt_master_password,
    prompt_master_password_new,
)

__all__ = [
    "build_parser",
    "ensure_vault_unlocked",
    "prompt_master_password",
    "prompt_master_password_new",
]
