"""Desktop platform implementation (Windows, macOS, Linux)."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import webbrowser

from pwm_platform.base import PlatformBase
from pwm.core.constants import VAULT_DIR, VAULT_FILE


class DesktopPlatform(PlatformBase):
    """Platform implementation for desktop OSes."""

    def get_vault_dir(self) -> str:
        return os.path.expanduser(VAULT_DIR)

    def get_vault_path(self) -> str:
        return os.path.expanduser(VAULT_FILE)

    def get_platform_name(self) -> str:
        return {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")

    def copy_to_clipboard(self, text: str) -> None:
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["clip.exe"],
                    input=text,
                    encoding="utf-8",
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                    if hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0,
                )
            elif sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=text, encoding="utf-8", check=True)
            else:
                if self._has_cmd("wl-copy"):
                    subprocess.run(["wl-copy"], input=text, encoding="utf-8", check=True)
                elif self._has_cmd("xclip"):
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=text,
                        encoding="utf-8",
                        check=True,
                    )
        except Exception:
            pass  # Clipboard is best-effort

    def clear_clipboard(self) -> None:
        self.copy_to_clipboard("")

    def read_clipboard(self) -> str:
        try:
            if sys.platform == "win32":
                r = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard"],
                    capture_output=True,
                    encoding="utf-8",
                    timeout=5,
                )
                return r.stdout if r.returncode == 0 else ""
            elif sys.platform == "darwin":
                r = subprocess.run(["pbpaste"], capture_output=True, encoding="utf-8", timeout=5)
                return r.stdout if r.returncode == 0 else ""
            else:
                if self._has_cmd("wl-paste"):
                    r = subprocess.run(["wl-paste"], capture_output=True, encoding="utf-8", timeout=5)
                    return r.stdout if r.returncode == 0 else ""
                elif self._has_cmd("xclip"):
                    r = subprocess.run(
                        ["xclip", "-selection", "clipboard", "-o"],
                        capture_output=True,
                        encoding="utf-8",
                        timeout=5,
                    )
                    return r.stdout if r.returncode == 0 else ""
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
                if current.strip() == original_text.strip():
                    self.clear_clipboard()
            except Exception:
                self.clear_clipboard()

        t = threading.Thread(target=_clear, daemon=True)
        t.start()

    def open_url(self, url: str) -> None:
        webbrowser.open(url)

    def show_notification(self, title: str, message: str) -> None:
        try:
            if sys.platform == "win32":
                from plyer import notification
                notification.notify(title=title, message=message, timeout=3)
            elif sys.platform == "darwin":
                subprocess.run(
                    ["osascript", "-e",
                     f'display notification "{message}" with title "{title}"'],
                    timeout=5,
                )
            else:
                subprocess.run(
                    ["notify-send", title, message], timeout=5
                )
        except Exception:
            pass

    @staticmethod
    def _has_cmd(cmd: str) -> bool:
        import shutil
        return shutil.which(cmd) is not None
