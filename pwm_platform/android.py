"""Android platform implementation."""

from __future__ import annotations

import os
import threading
import time

from pwm_platform.base import PlatformBase


class AndroidPlatform(PlatformBase):
    """Platform implementation for Android (via Kivy / pyjnius)."""

    def __init__(self):
        self._activity = None
        self._context = None
        self._clipboard_service = None
        self._PowerManager = None
        try:
            from jnius import autoclass
            self._activity = autoclass("org.kivy.android.PythonActivity").mActivity
            self._context = self._activity.getApplicationContext()
            self._clipboard_service = self._context.getSystemService(
                self._context.CLIPBOARD_SERVICE
            )
            self._PowerManager = autoclass("android.os.PowerManager")
        except Exception:
            pass

    def get_vault_dir(self) -> str:
        try:
            if self._context:
                files_dir = self._context.getFilesDir().getAbsolutePath()
                vault_dir = os.path.join(files_dir, ".pwm")
                os.makedirs(vault_dir, exist_ok=True)
                return vault_dir
        except Exception:
            pass
        return "/data/data/org.pwm.app/files/.pwm"

    def get_vault_path(self) -> str:
        return os.path.join(self.get_vault_dir(), "vault.json")

    def get_platform_name(self) -> str:
        return "Android"

    def copy_to_clipboard(self, text: str) -> None:
        try:
            from jnius import autoclass
            ClipData = autoclass("android.content.ClipData")
            clip = ClipData.newPlainText("PWM Password", text)
            self._clipboard_service.setPrimaryClip(clip)
        except Exception:
            pass

    def clear_clipboard(self) -> None:
        self.copy_to_clipboard("")

    def read_clipboard(self) -> str:
        try:
            clip = self._clipboard_service.getPrimaryClip()
            if clip and clip.getItemCount() > 0:
                return clip.getItemAt(0).getText().toString() or ""
        except Exception:
            pass
        return ""

    def schedule_clipboard_clear(self, delay_seconds: int, original_text: str) -> None:
        if delay_seconds <= 0:
            return

        def _clear():
            time.sleep(delay_seconds)
            try:
                current = self.read_clipboard()
                if current == original_text:
                    self.clear_clipboard()
            except Exception:
                pass

        t = threading.Thread(target=_clear, daemon=True)
        t.start()

    def open_url(self, url: str) -> None:
        try:
            from jnius import autoclass, cast
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            intent.addFlags(0x10000000)  # FLAG_ACTIVITY_NEW_TASK
            self._context.startActivity(intent)
        except Exception:
            pass

    def show_notification(self, title: str, message: str) -> None:
        try:
            from jnius import autoclass
            NotificationBuilder = autoclass("android.app.Notification$Builder")
            NotificationManager = autoclass("android.app.NotificationManager")
            # Minimal notification
            nm = self._context.getSystemService("notification")
        except Exception:
            pass

    def secure_storage_available(self) -> bool:
        return True  # Android has keystore
