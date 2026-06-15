"""PWM — Cross-platform GUI application (Kivy-based)."""

from __future__ import annotations

import os
import sys
import time

# Ensure pwm package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from pwm_platform import Platform as P
from pwm.core import vault
from pwm.core.models import Account
from pwm.core.exceptions import (
    WrongPasswordError,
    VaultLockedError,
    VaultNotFoundError,
    AccountNotFoundError,
    AccountDuplicateError,
)
from pwm.utils.generator import generate_password, password_strength
from pwm._version import __version__


# ── Color scheme ──────────────────────────────────────────────────────────────
COLORS = {
    "bg": (0.05, 0.08, 0.15, 1),
    "card": (0.10, 0.14, 0.22, 1),
    "primary": (0.10, 0.45, 0.91, 1),
    "accent": (1.0, 0.70, 0.0, 1),
    "text": (0.92, 0.93, 0.95, 1),
    "muted": (0.55, 0.58, 0.65, 1),
    "danger": (0.85, 0.15, 0.15, 1),
    "success": (0.15, 0.72, 0.35, 1),
    "white": (1, 1, 1, 1),
}


class PwmApp(App):
    """Main PWM application."""

    title = "PWM Password Manager"

    def build(self):
        Window.clearcolor = COLORS["bg"]
        Window.minimum_width = 360
        Window.minimum_height = 600

        self.platform = P()
        self.auto_lock_event = None

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(UnlockScreen(name="unlock"))
        sm.add_widget(VaultScreen(name="vault"))
        sm.add_widget(DetailScreen(name="detail"))
        sm.add_widget(AddEditScreen(name="add_edit"))
        sm.add_widget(GeneratorScreen(name="generator"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

    def on_start(self):
        vault_path = self.platform.get_vault_path()
        if os.path.exists(vault_path):
            self.root.current = "unlock"
        else:
            # No vault yet — go directly to init
            self.root.get_screen("unlock").ids.status_label.text = "Create a new vault"
            self.root.get_screen("unlock").mode = "create"

    def start_auto_lock_timer(self):
        self.cancel_auto_lock()
        cfg = vault.get_config()
        if cfg.auto_lock_timeout > 0:
            self.auto_lock_event = Clock.schedule_once(
                self._auto_lock, cfg.auto_lock_timeout
            )

    def cancel_auto_lock(self):
        if self.auto_lock_event:
            self.auto_lock_event.cancel()
            self.auto_lock_event = None

    def _auto_lock(self, dt):
        if vault.is_unlocked():
            vault.lock_vault()
        self.root.current = "unlock"
        self.root.get_screen("unlock").ids.status_label.text = "Vault auto-locked. Enter master password."

    def show_popup(self, title: str, message: str, on_dismiss=None):
        content = BoxLayout(orientation="vertical", padding=20, spacing=15)
        content.add_widget(Label(
            text=message,
            color=COLORS["text"],
            halign="center",
            text_size=(Window.width * 0.7, None),
        ))
        btn = Button(
            text="OK",
            size_hint=(1, None),
            height=48,
            background_color=COLORS["primary"],
            color=COLORS["white"],
        )
        content.add_widget(btn)
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=True,
            background_color=COLORS["card"],
            title_color=COLORS["text"],
        )
        btn.bind(on_release=popup.dismiss)
        if on_dismiss:
            popup.bind(on_dismiss=on_dismiss)
        popup.open()


# ── Screens ───────────────────────────────────────────────────────────────────

class UnlockScreen(Screen):
    mode = StringProperty("unlock")  # "unlock" or "create"
    status_text = StringProperty("Enter your master password")

    def do_action(self):
        pw = self.ids.password_input.text
        if not pw:
            self.status_text = "Please enter a password."
            return

        vault_path = app().platform.get_vault_path()

        try:
            if self.mode == "create":
                if len(pw) < 8:
                    self.status_text = "Master password must be at least 8 characters."
                    return
                vault.init_vault(pw, vault_path)
                self.status_text = "Vault created!"
            else:
                vault.unlock_vault(pw, vault_path)
                self.status_text = "Unlocked!"
        except VaultNotFoundError:
            self.status_text = "No vault found. Create one first."
            self.mode = "create"
            return
        except WrongPasswordError:
            self.status_text = "Incorrect password. Try again."
            return
        except Exception as e:
            self.status_text = str(e)
            return

        self.ids.password_input.text = ""
        self.manager.current = "vault"

    def toggle_mode(self):
        self.mode = "create" if self.mode == "unlock" else "unlock"
        self.status_text = (
            "Create a master password (min 8 chars)"
            if self.mode == "create"
            else "Enter your master password"
        )


class VaultScreen(Screen):
    accounts = ListProperty([])
    search_query = StringProperty("")
    filtered_accounts = ListProperty([])

    def on_enter(self, *args):
        app().start_auto_lock_timer()
        self.refresh()

    def on_leave(self, *args):
        app().cancel_auto_lock()

    def refresh(self):
        try:
            self.accounts = vault.get_accounts()
            self.apply_filter()
        except VaultLockedError:
            self.manager.current = "unlock"

    def apply_filter(self):
        q = self.search_query.lower()
        if q:
            self.filtered_accounts = [
                a for a in self.accounts
                if q in a.service.lower() or q in a.category.lower()
            ]
        else:
            self.filtered_accounts = list(self.accounts)

    def on_search(self, text):
        self.search_query = text
        self.apply_filter()

    def open_detail(self, account_index):
        acc = self.filtered_accounts[account_index]
        self.manager.get_screen("detail").account = acc
        self.manager.current = "detail"

    def add_account(self):
        self.manager.get_screen("add_edit").account = None  # None = new
        self.manager.current = "add_edit"

    def lock_vault(self):
        vault.lock_vault()
        self.manager.get_screen("unlock").ids.status_label.text = "Enter your master password"
        self.manager.get_screen("unlock").mode = "unlock"
        self.manager.current = "unlock"

    def open_generator(self):
        self.manager.current = "generator"

    def open_settings(self):
        self.manager.current = "settings"


class DetailScreen(Screen):
    account = ObjectProperty(None)

    def on_account(self, instance, value):
        if value:
            self.ids.service_label.text = value.service
            self.ids.username_label.text = value.username
            self.ids.password_label.text = value.password
            self.ids.notes_label.text = value.notes or "—"
            self.ids.category_label.text = value.category or "—"

    def copy_password(self):
        if self.account:
            app().platform.copy_to_clipboard(self.account.password)
            app().platform.schedule_clipboard_clear(30, self.account.password)
            app().show_popup("Copied", "Password copied to clipboard.\nClears in 30s.")

    def copy_username(self):
        if self.account:
            app().platform.copy_to_clipboard(self.account.username)
            app().show_popup("Copied", "Username copied to clipboard.")

    def open_url(self):
        if self.account:
            # Build URL from service if it looks like a domain
            svc = self.account.service
            if not svc.startswith("http"):
                url = f"https://{svc}"
            else:
                url = svc
            app().platform.open_url(url)

    def edit_account(self):
        self.manager.get_screen("add_edit").account = self.account
        self.manager.current = "add_edit"

    def delete_account(self):
        acc = self.account
        def do_delete(instance):
            try:
                vault.delete_account(acc.service)
            except AccountNotFoundError:
                pass
            self.manager.current = "vault"
        app().show_popup(
            "Delete?",
            f"Delete '{acc.service}'?\nThis cannot be undone.",
            on_dismiss=lambda _: do_delete(None),
        )


class AddEditScreen(Screen):
    account = ObjectProperty(None)  # None = new, Account = edit
    is_edit = BooleanProperty(False)

    def on_account(self, instance, value):
        self.is_edit = value is not None
        if value:
            self.ids.service_input.text = value.service
            self.ids.username_input.text = value.username
            self.ids.password_input.text = value.password
            self.ids.notes_input.text = value.notes or ""
            self.ids.category_input.text = value.category or ""

    def generate_password(self):
        pw = generate_password(length=20)
        self.ids.password_input.text = pw
        strength = password_strength(pw)
        app().show_popup(
            "Password Generated",
            f"Length: {strength['length']} chars\n"
            f"Strength: {strength['rating']}\n"
            f"Entropy: ~{strength['entropy_estimate']} bits",
        )

    def save(self):
        service = self.ids.service_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        notes = self.ids.notes_input.text.strip()
        category = self.ids.category_input.text.strip()

        if not service:
            app().show_popup("Error", "Service name is required.")
            return
        if not username:
            app().show_popup("Error", "Username is required.")
            return
        if not password:
            app().show_popup("Error", "Password is required.")
            return

        try:
            if self.is_edit:
                vault.update_account(self.account.service, {
                    "service": service,
                    "username": username,
                    "password": password,
                    "notes": notes,
                    "category": category,
                })
            else:
                vault.add_account(Account(
                    service=service,
                    username=username,
                    password=password,
                    notes=notes,
                    category=category,
                ))
        except AccountDuplicateError:
            app().show_popup("Error", f"Account '{service}' already exists.")
            return
        except Exception as e:
            app().show_popup("Error", str(e))
            return

        self.manager.current = "vault"


class GeneratorScreen(Screen):
    password = StringProperty("")
    length = StringProperty("20")
    strength_text = StringProperty("")

    def generate(self):
        try:
            length = int(self.length)
        except ValueError:
            length = 20
        pw = generate_password(
            length=length,
            upper=self.ids.upper_toggle.active,
            lower=self.ids.lower_toggle.active,
            digits=self.ids.digits_toggle.active,
            symbols=self.ids.symbols_toggle.active,
            easy_mode=self.ids.easy_toggle.active,
        )
        self.password = pw
        s = password_strength(pw)
        self.strength_text = (
            f"Length: {s['length']} | Entropy: ~{s['entropy_estimate']} bits | "
            f"Rating: {s['rating'].upper()}"
        )

    def copy_password(self):
        if self.password:
            app().platform.copy_to_clipboard(self.password)
            app().show_popup("Copied", "Password copied to clipboard.")

    def use_in_add(self):
        if self.password:
            self.manager.get_screen("add_edit").ids.password_input.text = self.password
            self.manager.current = "add_edit"


class SettingsScreen(Screen):
    config = ObjectProperty(None)

    def on_enter(self, *args):
        try:
            self.config = vault.get_config()
            self.ids.lock_timeout.text = str(self.config.auto_lock_timeout)
            self.ids.clipboard_timeout.text = str(self.config.clipboard_clear_timeout)
            self.ids.max_attempts.text = str(self.config.max_failed_attempts)
            self.ids.lockout_duration.text = str(self.config.lockout_duration)
        except VaultLockedError:
            self.manager.current = "unlock"

    def save_settings(self):
        try:
            vault.set_config({
                "auto_lock_timeout": int(self.ids.lock_timeout.text),
                "clipboard_clear_timeout": int(self.ids.clipboard_timeout.text),
                "max_failed_attempts": int(self.ids.max_attempts.text),
                "lockout_duration": int(self.ids.lockout_duration.text),
            })
            app().show_popup("Saved", "Settings updated.")
        except Exception as e:
            app().show_popup("Error", str(e))

    def change_master_password(self):
        # Navigate to unlock with "change" mode
        pass

    def export_vault(self):
        from pwm_platform import _PLATFORM
        if _PLATFORM == "android":
            export_path = "/sdcard/Download/pwm_backup.pwmbackup"
        else:
            export_path = os.path.expanduser("~/pwm_backup.pwmbackup")
        try:
            vault.export_vault(export_path)
            app().show_popup("Exported", f"Backup saved to:\n{export_path}")
        except Exception as e:
            app().show_popup("Error", str(e))


def app() -> PwmApp:
    """Get the running PwmApp instance."""
    return App.get_running_app()
