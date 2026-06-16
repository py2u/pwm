"""Tests for vault lifecycle management."""

import os
import tempfile
import pytest
from pwm.core import vault
from pwm.core.models import Account
from pwm.core.exceptions import (
    VaultAlreadyExistsError,
    VaultNotFoundError,
    WrongPasswordError,
    VaultLockedError,
    LockoutError,
    AccountNotFoundError,
    AccountDuplicateError,
)


@pytest.fixture
def temp_vault():
    """Create a temporary vault for testing, clean up after."""
    path = os.path.join(tempfile.gettempdir(), f"pwm_test_{os.urandom(4).hex()}.json")
    vault.init_vault("test_master", path)
    yield path
    vault.lock_vault()
    try:
        os.remove(path)
    except OSError:
        pass


class TestVaultLifecycle:
    """Test vault initialization, unlock, lock."""

    def test_init_creates_file(self, temp_vault):
        """init should create a vault file on disk."""
        assert os.path.exists(temp_vault)

    def test_init_duplicate_fails(self, temp_vault):
        """init should fail if vault already exists."""
        with pytest.raises(VaultAlreadyExistsError):
            vault.init_vault("another_password", temp_vault)

    def test_unlock_with_correct_password(self, temp_vault):
        """Unlock should work with correct password."""
        vault.lock_vault()
        vault.unlock_vault("test_master", temp_vault)
        assert vault.is_unlocked()

    def test_unlock_with_wrong_password(self, temp_vault):
        """Unlock should fail with wrong password."""
        vault.lock_vault()
        with pytest.raises(WrongPasswordError):
            vault.unlock_vault("wrong_password", temp_vault)

    def test_lock_vault(self, temp_vault):
        """Lock should clear session state."""
        vault.lock_vault()
        with pytest.raises(VaultLockedError):
            vault.get_accounts()

    def test_get_accounts_requires_unlock(self, temp_vault):
        """get_accounts should fail if vault is locked."""
        vault.lock_vault()
        with pytest.raises(VaultLockedError):
            vault.get_accounts()


class TestAccountCRUD:
    """Test account CRUD operations."""

    def test_add_account(self, temp_vault):
        """Should successfully add an account."""
        acc = Account(service="example.com", username="user", password="pass123")
        vault.add_account(acc)
        accounts = vault.get_accounts()
        assert len(accounts) == 1
        assert accounts[0].service == "example.com"

    def test_add_duplicate_fails(self, temp_vault):
        """Adding duplicate service name should fail."""
        vault.add_account(Account(service="example.com", username="u", password="p"))
        with pytest.raises(AccountDuplicateError):
            vault.add_account(Account(service="Example.COM", username="u2", password="p2"))

    def test_find_account(self, temp_vault):
        """Should find account by service name (case-insensitive)."""
        vault.add_account(Account(service="GitHub.com", username="user", password="pass"))
        acc = vault.find_account("github.com")
        assert acc.username == "user"

    def test_find_nonexistent_raises(self, temp_vault):
        """Should raise AccountNotFoundError for nonexistent service."""
        with pytest.raises(AccountNotFoundError):
            vault.find_account("nonexistent.com")

    def test_update_account(self, temp_vault):
        """Should update account fields."""
        vault.add_account(Account(service="example.com", username="old", password="old"))
        updated = vault.update_account("example.com", {"username": "new_user", "category": "test"})
        assert updated.username == "new_user"
        assert updated.category == "test"

    def test_rename_to_duplicate_service_fails(self, temp_vault):
        """Renaming an account should not create duplicate service names."""
        vault.add_account(Account(service="one.com", username="u1", password="p1"))
        vault.add_account(Account(service="two.com", username="u2", password="p2"))

        with pytest.raises(AccountDuplicateError):
            vault.update_account("one.com", {"service": "TWO.com"})

        assert [a.service for a in vault.get_accounts()] == ["one.com", "two.com"]

    def test_delete_account(self, temp_vault):
        """Should delete an account."""
        vault.add_account(Account(service="example.com", username="u", password="p"))
        vault.delete_account("example.com")
        assert len(vault.get_accounts()) == 0

    def test_delete_nonexistent_raises(self, temp_vault):
        """Deleting nonexistent account should raise."""
        with pytest.raises(AccountNotFoundError):
            vault.delete_account("nonexistent.com")

    def test_search_accounts(self, temp_vault):
        """Search should find by service name and category."""
        vault.add_account(Account(service="github.com", username="u1", password="p1", category="dev"))
        vault.add_account(Account(service="google.com", username="u2", password="p2", category="work"))
        vault.add_account(Account(service="netflix.com", username="u3", password="p3", category="fun"))

        results = vault.search_accounts("git")
        assert len(results) == 1
        assert results[0].service == "github.com"

        results = vault.search_accounts("work")
        assert len(results) == 1
        assert results[0].service == "google.com"

        results = vault.search_accounts("xyz")
        assert len(results) == 0


class TestLockout:
    """Test failed attempt lockout mechanism."""

    def test_lockout_after_max_attempts(self, temp_vault):
        """Should lock out after max_failed_attempts wrong passwords."""
        vault.set_config({"max_failed_attempts": 3, "lockout_duration": 5})
        vault.lock_vault()

        # 2 wrong attempts should give WrongPasswordError
        for _ in range(2):
            with pytest.raises(WrongPasswordError):
                vault.unlock_vault("wrong", temp_vault)

        # 3rd wrong attempt should trigger LockoutError
        with pytest.raises(LockoutError):
            vault.unlock_vault("wrong3", temp_vault)


class TestImportExport:
    """Test vault export and import."""

    def test_export_then_import(self, temp_vault):
        """Export and import should preserve accounts."""
        vault.add_account(Account(service="example.com", username="u", password="p"))
        vault.lock_vault()

        export_path = temp_vault + ".backup"
        vault.unlock_vault("test_master", temp_vault)
        vault.export_vault(export_path, temp_vault)
        assert os.path.exists(export_path)

        # Import as replace
        vault.delete_account("example.com")
        assert len(vault.get_accounts()) == 0

        count = vault.import_vault(export_path, mode="replace")
        assert count == 1
        assert len(vault.get_accounts()) == 1

        os.remove(export_path)

    def test_import_same_master_password_different_salt(self):
        """Import should work when vaults share a master password but have different salts."""
        source_path = os.path.join(tempfile.gettempdir(), f"pwm_src_{os.urandom(4).hex()}.json")
        dest_path = os.path.join(tempfile.gettempdir(), f"pwm_dest_{os.urandom(4).hex()}.json")
        export_path = source_path + ".backup"

        try:
            vault.init_vault("same_master", source_path)
            vault.add_account(Account(service="example.com", username="u", password="p"))
            vault.export_vault(export_path, source_path)
            vault.lock_vault()

            vault.init_vault("same_master", dest_path)
            count = vault.import_vault(export_path, mode="merge", master_password="same_master")

            assert count == 1
            assert vault.find_account("example.com").username == "u"
        finally:
            vault.lock_vault()
            for path in (source_path, dest_path, export_path):
                try:
                    os.remove(path)
                except OSError:
                    pass


class TestConfig:
    """Test configuration management."""

    def test_get_config(self, temp_vault):
        """Should return default config."""
        cfg = vault.get_config()
        assert cfg.auto_lock_timeout == 300
        assert cfg.clipboard_clear_timeout == 30

    def test_set_config(self, temp_vault):
        """Should update config values."""
        vault.set_config({"auto_lock_timeout": 120, "clipboard_clear_timeout": 10})
        cfg = vault.get_config()
        assert cfg.auto_lock_timeout == 120
        assert cfg.clipboard_clear_timeout == 10


class TestChangePassword:
    """Test master password change."""

    def test_change_password(self, temp_vault):
        """Should be able to change master password."""
        vault.lock_vault()
        vault.unlock_vault("test_master", temp_vault)
        vault.change_master_password("new_master_5678")
        vault.lock_vault()

        # Old password should fail
        with pytest.raises(WrongPasswordError):
            vault.unlock_vault("test_master", temp_vault)

        # New password should work
        vault.unlock_vault("new_master_5678", temp_vault)
        assert vault.is_unlocked()
