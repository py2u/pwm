from __future__ import annotations

"""Cross-platform clipboard operations with auto-clear functionality."""

import subprocess
import sys
import threading
import time

from pwm.core.exceptions import ClipboardError


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard.

    Platform detection:
        Windows: clip.exe
        macOS: pbcopy
        Linux: xclip or wl-copy
    """
    platform = sys.platform

    try:
        if platform == "win32":
            # Windows: pipe to clip.exe
            proc = subprocess.run(
                ["clip.exe"],
                input=text,
                encoding="utf-8",
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
        elif platform == "darwin":
            proc = subprocess.run(
                ["pbcopy"],
                input=text,
                encoding="utf-8",
                check=True,
            )
        else:
            # Linux: try wl-copy (Wayland) first, then xclip (X11)
            if _has_command("wl-copy"):
                proc = subprocess.run(
                    ["wl-copy"],
                    input=text,
                    encoding="utf-8",
                    check=True,
                )
            elif _has_command("xclip"):
                proc = subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text,
                    encoding="utf-8",
                    check=True,
                )
            else:
                raise ClipboardError()
    except FileNotFoundError:
        raise ClipboardError()
    except subprocess.CalledProcessError:
        raise ClipboardError()


def clear_clipboard() -> None:
    """Clear the system clipboard (set to empty string)."""
    try:
        copy_to_clipboard("")
    except ClipboardError:
        pass


def _has_command(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    import shutil
    return shutil.which(cmd) is not None


def schedule_clipboard_clear(delay_seconds: int, original_text: str | None = None) -> threading.Thread | None:
    """Schedule clipboard clearing after a delay.

    Args:
        delay_seconds: Seconds to wait before clearing.
        original_text: If provided, only clear if clipboard still contains this text.

    Returns:
        The background thread, or None if delay is 0.
    """
    if delay_seconds <= 0:
        return None

    def _clear_after_delay():
        time.sleep(delay_seconds)
        if original_text is not None:
            # Only clear if clipboard still has our password
            try:
                current = _read_clipboard()
                if current.strip() != original_text.strip():
                    return  # User has copied something else, leave it
            except Exception:
                pass  # Can't read clipboard, clear unconditionally
        clear_clipboard()

    thread = threading.Thread(target=_clear_after_delay, daemon=True)
    thread.start()
    return thread


def _read_clipboard() -> str:
    """Read the current clipboard content.

    Returns empty string if clipboard can't be read.
    """
    platform = sys.platform
    try:
        if platform == "win32":
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True,
                encoding="utf-8",
                timeout=5,
            )
            return result.stdout if result.returncode == 0 else ""
        elif platform == "darwin":
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                encoding="utf-8",
                timeout=5,
            )
            return result.stdout if result.returncode == 0 else ""
        else:
            if _has_command("wl-paste"):
                result = subprocess.run(
                    ["wl-paste"],
                    capture_output=True,
                    encoding="utf-8",
                    timeout=5,
                )
                return result.stdout if result.returncode == 0 else ""
            elif _has_command("xclip"):
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True,
                    encoding="utf-8",
                    timeout=5,
                )
                return result.stdout if result.returncode == 0 else ""
    except Exception:
        pass
    return ""
