from __future__ import annotations

"""CLI argument parsing and command handlers for the PWM password manager."""

import argparse
import getpass
import sys
import time

from pwm.core.constants import (
    VAULT_FILE,
    DEFAULT_PASSWORD_LENGTH,
)
from pwm.core.models import Account
from pwm.core.exceptions import (
    PwmError,
    VaultNotFoundError,
    VaultAlreadyExistsError,
    WrongPasswordError,
    VaultLockedError,
    LockoutError,
    AccountNotFoundError,
    AccountDuplicateError,
    ClipboardError,
    ConfigError,
)
from pwm.core import vault
from pwm.utils.generator import generate_password, password_strength
from pwm.utils.clipboard import copy_to_clipboard, schedule_clipboard_clear


# ---------------------------------------------------------------------------
# Master password prompting
# ---------------------------------------------------------------------------

def prompt_master_password(prompt_text: str = "Master password: ") -> str:
    """Securely prompt for the master password (input is hidden)."""
    return getpass.getpass(prompt_text)


def prompt_master_password_new() -> str:
    """Prompt for a new master password with confirmation."""
    while True:
        pw1 = getpass.getpass("New master password: ")
        if len(pw1) < 4:
            print("Password must be at least 4 characters.")
            continue
        pw2 = getpass.getpass("Confirm master password: ")
        if pw1 == pw2:
            return pw1
        print("Passwords do not match. Please try again.")


def ensure_vault_unlocked(vault_path: str | None = None) -> None:
    """Ensure the vault is unlocked, prompting for password if needed.

    This is the main entry guard for all commands that need an unlocked vault.
    """
    if vault.is_unlocked():
        return

    # Vault is locked — prompt for password
    path = vault_path or VAULT_FILE
    while True:
        pw = prompt_master_password()
        try:
            vault.unlock_vault(pw, path)
            print("Vault unlocked.")
            return
        except VaultNotFoundError:
            print(f"No vault found at: {path}")
            print("Run 'pwm init' to create a new vault.")
            sys.exit(1)
        except LockoutError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except WrongPasswordError as e:
            print(f"Error: {e}")
            # If remaining <= 0, the next loop iteration will hit LockoutError
        except PwmError as e:
            print(f"Error: {e}")
            sys.exit(1)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_account_table(accounts: list[Account], show_passwords: bool = False) -> None:
    """Print accounts in a formatted table."""
    if not accounts:
        print("No accounts found.")
        return

    # Calculate column widths
    svc_w = max(12, max((len(a.service) for a in accounts), default=12))
    usr_w = max(12, max((len(a.username) for a in accounts), default=12))
    cat_w = max(8, max((len(a.category) for a in accounts), default=8))

    # Header
    header = f"  {'Service':<{svc_w}}  {'Username':<{usr_w}}  {'Password':<16}  {'Category':<{cat_w}}  Updated"
    print(header)
    print("-" * len(header))

    for acc in accounts:
        pw_display = acc.password if show_passwords else "********"
        updated = time.strftime("%Y-%m-%d", time.localtime(acc.updated_at)) if acc.updated_at else "-"
        print(f"  {acc.service:<{svc_w}}  {acc.username:<{usr_w}}  {pw_display:<16}  {acc.category:<{cat_w}}  {updated}")


def _print_account_detail(account: Account) -> None:
    """Print full details for a single account."""
    print(f"Service:   {account.service}")
    print(f"Username:  {account.username}")
    print(f"Password:  {account.password}")
    if account.category:
        print(f"Category:  {account.category}")
    if account.notes:
        print(f"Notes:     {account.notes}")
    if account.created_at:
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(account.created_at))
        print(f"Created:   {created}")
    if account.updated_at:
        updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(account.updated_at))
        print(f"Updated:   {updated}")


def _prompt_interactive(service: str | None = None) -> dict:
    """Interactively prompt for account fields. Returns a dict suitable for Account creation."""
    if not service:
        service = input("Service name: ").strip()
        if not service:
            print("Service name is required.")
            sys.exit(1)

    username = input("Username: ").strip()
    if not username:
        print("Username is required.")
        sys.exit(1)

    password = getpass.getpass("Password (leave blank to generate): ")
    if not password:
        print("Generating password...")
        password = generate_password()
        print(f"Generated password: {password}")

    notes = input("Notes (optional): ").strip()
    category = input("Category (optional): ").strip()

    return {
        "service": service,
        "username": username,
        "password": password,
        "notes": notes,
        "category": category,
    }


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new password vault."""
    path = args.vault or VAULT_FILE
    print(f"Initializing new vault at: {path}")
    print("Choose a strong master password — it protects all your stored credentials.")
    master_pw = prompt_master_password_new()
    try:
        created_path = vault.init_vault(master_pw, path)
        print(f"\nVault created successfully at: {created_path}")
        print("You can now add accounts with: pwm add")
    except VaultAlreadyExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new account."""
    ensure_vault_unlocked(args.vault)

    # Determine fields
    if args.service and args.username:
        service = args.service
        username = args.username
        if args.generate:
            password = generate_password(easy_mode=args.easy)
            print(f"Generated password: {password}")
        elif args.password:
            password = args.password
        else:
            password = getpass.getpass("Password (input hidden): ")
        notes = args.notes or ""
        category = args.category or ""
    elif args.service and not args.username:
        # Partial interactive
        fields = _prompt_interactive(service=args.service)
        fields["username"] = args.username or fields["username"]
        fields["password"] = args.password or fields["password"]
        fields["notes"] = args.notes or fields["notes"]
        fields["category"] = args.category or fields["category"]
        service = fields["service"]
        username = fields["username"]
        password = fields["password"]
        notes = fields["notes"]
        category = fields["category"]
    else:
        # Fully interactive
        fields = _prompt_interactive()
        service = fields["service"]
        username = fields["username"]
        password = fields["password"]
        notes = fields["notes"]
        category = fields["category"]

    account = Account(
        service=service,
        username=username,
        password=password,
        notes=notes,
        category=category,
    )

    try:
        vault.add_account(account)
        print(f"Account '{service}' added.")
        vault.touch_activity()
    except AccountDuplicateError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List all accounts."""
    ensure_vault_unlocked(args.vault)
    accounts = vault.get_accounts()
    if args.category:
        accounts = [a for a in accounts if a.category.lower() == args.category.lower()]
    _print_account_table(accounts, show_passwords=args.show_passwords)
    vault.touch_activity()


def cmd_show(args: argparse.Namespace) -> None:
    """Show full details for a single account."""
    ensure_vault_unlocked(args.vault)
    try:
        account = vault.find_account(args.service)
        _print_account_detail(account)
        vault.touch_activity()

        # Copy password to clipboard unless --no-copy is specified
        if not args.no_copy:
            try:
                copy_to_clipboard(account.password)
                timeout = vault.get_config().clipboard_clear_timeout
                schedule_clipboard_clear(timeout, account.password)
                print(f"\nPassword copied to clipboard. Will be cleared in {timeout}s.")
            except ClipboardError as e:
                print(f"\nWarning: Could not copy to clipboard: {e}")
    except AccountNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_edit(args: argparse.Namespace) -> None:
    """Edit an existing account."""
    ensure_vault_unlocked(args.vault)
    try:
        updates = {}
        if args.new_service:
            updates["service"] = args.new_service
        if args.username:
            updates["username"] = args.username
        if args.generate:
            new_pw = generate_password(easy_mode=args.easy)
            updates["password"] = new_pw
            print(f"Generated new password: {new_pw}")
        elif args.password:
            updates["password"] = args.password
        if args.notes is not None:
            updates["notes"] = args.notes
        if args.category is not None:
            updates["category"] = args.category

        if not updates:
            print("No changes specified. Use --username, --password, --generate, --notes, --category, or --service.")
            sys.exit(1)

        account = vault.update_account(args.service, updates)
        print(f"Account '{account.service}' updated.")
        vault.touch_activity()
    except AccountNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete an account."""
    ensure_vault_unlocked(args.vault)
    try:
        if not args.force:
            confirm = input(f"Are you sure you want to delete '{args.service}'? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Cancelled.")
                return
        vault.delete_account(args.service)
        print(f"Account '{args.service}' deleted.")
        vault.touch_activity()
    except AccountNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_search(args: argparse.Namespace) -> None:
    """Search accounts by service name or category."""
    ensure_vault_unlocked(args.vault)
    results = vault.search_accounts(args.query, category_only=args.category_only)
    if results:
        print(f"Found {len(results)} matching account(s):")
        _print_account_table(results, show_passwords=args.show_passwords)
    else:
        print(f"No accounts matching '{args.query}'.")
    vault.touch_activity()


def cmd_gen(args: argparse.Namespace) -> None:
    """Generate a random password."""
    pw = generate_password(
        length=args.length,
        upper=not args.no_upper,
        lower=not args.no_lower,
        digits=not args.no_digits,
        symbols=not args.no_symbols,
        easy_mode=args.easy,
    )
    strength = password_strength(pw)
    print(f"Password:  {pw}")
    print(f"Length:    {strength['length']} chars")
    print(f"Entropy:   ~{strength['entropy_estimate']} bits")
    print(f"Strength:  {strength['rating']}")

    # Copy to clipboard if requested
    if args.copy:
        try:
            copy_to_clipboard(pw)
            print(f"\nPassword copied to clipboard.")
        except ClipboardError as e:
            print(f"\nWarning: Could not copy to clipboard: {e}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export an encrypted vault backup."""
    ensure_vault_unlocked(args.vault)
    try:
        export_path = vault.export_vault(args.path, args.vault)
        print(f"Encrypted vault exported to: {export_path}")
        vault.touch_activity()
    except PwmError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_import(args: argparse.Namespace) -> None:
    """Import an encrypted vault backup."""
    ensure_vault_unlocked(args.vault)
    mode = "replace" if args.replace else "merge"
    import_password = prompt_master_password("Master password for imported vault: ")
    try:
        count = vault.import_vault(args.path, mode=mode, master_password=import_password)
        action = "Replaced all accounts with" if mode == "replace" else f"Imported {count} new account(s) from"
        print(f"{action}: {args.path}")
        vault.touch_activity()
    except WrongPasswordError:
        print("Error: The imported vault was created with a different master password.")
        print("Both vaults must use the same master password for import.")
        sys.exit(1)
    except PwmError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_lock(args: argparse.Namespace) -> None:
    """Manually lock the vault."""
    if vault.is_unlocked():
        vault.lock_vault()
        print("Vault locked.")
    else:
        print("Vault is already locked.")


def cmd_config(args: argparse.Namespace) -> None:
    """View or change vault configuration."""
    ensure_vault_unlocked(args.vault)

    if args.set:
        key, value = args.set
        try:
            value = int(value)
            new_config = vault.set_config({key: value})
            print(f"  {key} = {getattr(new_config, key)}")
            vault.touch_activity()
        except ValueError:
            print(f"Error: Value for '{key}' must be an integer.")
            sys.exit(1)
        except ConfigError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        config = vault.get_config()
        print("Vault Configuration:")
        print(f"  auto_lock_timeout:       {config.auto_lock_timeout}s (0 = disabled)")
        print(f"  clipboard_clear_timeout: {config.clipboard_clear_timeout}s (0 = disabled)")
        print(f"  max_failed_attempts:     {config.max_failed_attempts}")
        print(f"  lockout_duration:        {config.lockout_duration}s")
        vault.touch_activity()


def cmd_changepw(args: argparse.Namespace) -> None:
    """Change the master password."""
    ensure_vault_unlocked(args.vault)
    print("Changing master password.")
    new_pw = prompt_master_password_new()
    vault.change_master_password(new_pw)
    print("Master password changed successfully.")
    vault.touch_activity()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the pwm CLI."""

    parser = argparse.ArgumentParser(
        prog="pwm",
        description="A secure, local CLI password manager.",
    )
    parser.add_argument(
        "--vault", "-V",
        default=None,
        help=f"Path to vault file (default: {VAULT_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", title="commands")

    # --- pwm init ---
    p_init = subparsers.add_parser("init", help="Initialize a new password vault")
    p_init.set_defaults(func=cmd_init)

    # --- pwm add ---
    p_add = subparsers.add_parser("add", help="Add a new account")
    p_add.add_argument("--service", "-s", help="Service name")
    p_add.add_argument("--username", "-u", help="Username / email")
    p_add.add_argument("--password", "-p", help="Password (omit for interactive prompt)")
    p_add.add_argument("--generate", "-g", action="store_true", help="Generate a random password")
    p_add.add_argument("--easy", "-e", action="store_true", help="Use easy-mode for generated password (no ambiguous chars)")
    p_add.add_argument("--notes", "-n", help="Notes")
    p_add.add_argument("--category", "-c", help="Category / tag")
    p_add.set_defaults(func=cmd_add)

    # --- pwm list ---
    p_list = subparsers.add_parser("list", help="List all accounts")
    p_list.add_argument("--category", "-c", help="Filter by category")
    p_list.add_argument("--show-passwords", "-P", action="store_true", help="Show passwords in plain text")
    p_list.set_defaults(func=cmd_list)

    # --- pwm show ---
    p_show = subparsers.add_parser("show", help="Show full account details")
    p_show.add_argument("service", help="Service name")
    p_show.add_argument("--no-copy", "-C", action="store_true", help="Do not copy password to clipboard")
    p_show.set_defaults(func=cmd_show)

    # --- pwm edit ---
    p_edit = subparsers.add_parser("edit", help="Edit an account")
    p_edit.add_argument("service", help="Service name")
    p_edit.add_argument("--service", "-s", dest="new_service", help="New service name")
    p_edit.add_argument("--username", "-u", help="New username")
    p_edit.add_argument("--password", "-p", help="New password")
    p_edit.add_argument("--generate", "-g", action="store_true", help="Generate a new password")
    p_edit.add_argument("--easy", "-e", action="store_true", help="Easy-mode for generated password")
    p_edit.add_argument("--notes", "-n", help="New notes (use '' to clear)")
    p_edit.add_argument("--category", "-c", help="New category")
    p_edit.set_defaults(func=cmd_edit)

    # --- pwm delete ---
    p_delete = subparsers.add_parser("delete", help="Delete an account")
    p_delete.add_argument("service", help="Service name")
    p_delete.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    p_delete.set_defaults(func=cmd_delete)

    # --- pwm search ---
    p_search = subparsers.add_parser("search", help="Search accounts")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--category-only", action="store_true", help="Search only in categories")
    p_search.add_argument("--show-passwords", "-P", action="store_true", help="Show passwords in plain text")
    p_search.set_defaults(func=cmd_search)

    # --- pwm gen ---
    p_gen = subparsers.add_parser("gen", help="Generate a random password")
    p_gen.add_argument("--length", "-l", type=int, default=DEFAULT_PASSWORD_LENGTH, help=f"Password length (default: {DEFAULT_PASSWORD_LENGTH})")
    p_gen.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters")
    p_gen.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters")
    p_gen.add_argument("--no-digits", action="store_true", help="Exclude digits")
    p_gen.add_argument("--no-symbols", action="store_true", help="Exclude symbols")
    p_gen.add_argument("--easy", "-e", action="store_true", help="Exclude ambiguous characters (O,0,l,1,etc.)")
    p_gen.add_argument("--copy", "-c", action="store_true", help="Copy generated password to clipboard")
    p_gen.set_defaults(func=cmd_gen)

    # --- pwm export ---
    p_export = subparsers.add_parser("export", help="Export encrypted vault backup")
    p_export.add_argument("path", help="Export file path")
    p_export.set_defaults(func=cmd_export)

    # --- pwm import ---
    p_import = subparsers.add_parser("import", help="Import encrypted vault backup")
    p_import.add_argument("path", help="Import file path")
    p_import.add_argument("--replace", "-r", action="store_true", help="Replace all accounts (default: merge)")
    p_import.set_defaults(func=cmd_import)

    # --- pwm lock ---
    p_lock = subparsers.add_parser("lock", help="Manually lock the vault")
    p_lock.set_defaults(func=cmd_lock)

    # --- pwm config ---
    p_config = subparsers.add_parser("config", help="View or change configuration")
    p_config.add_argument("--set", "-s", nargs=2, metavar=("KEY", "VALUE"), help="Set a config value")
    p_config.set_defaults(func=cmd_config)

    # --- pwm changepw ---
    p_changepw = subparsers.add_parser("changepw", help="Change master password")
    p_changepw.set_defaults(func=cmd_changepw)

    return parser
