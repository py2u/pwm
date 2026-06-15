"""Abstract platform interface for PWM."""

from abc import ABC, abstractmethod


class PlatformBase(ABC):
    """Defines the interface that each platform must implement."""

    @abstractmethod
    def get_vault_dir(self) -> str:
        """Return the directory where the vault file is stored."""
        ...

    @abstractmethod
    def get_vault_path(self) -> str:
        """Return the full path to the vault file."""
        ...

    @abstractmethod
    def copy_to_clipboard(self, text: str) -> None:
        """Copy text to the system clipboard."""
        ...

    @abstractmethod
    def clear_clipboard(self) -> None:
        """Clear the system clipboard."""
        ...

    @abstractmethod
    def read_clipboard(self) -> str:
        """Read text from the system clipboard."""
        ...

    @abstractmethod
    def schedule_clipboard_clear(self, delay_seconds: int, original_text: str) -> None:
        """Schedule clipboard clearing after a delay."""
        ...

    @abstractmethod
    def get_platform_name(self) -> str:
        """Return a human-readable platform name."""
        ...

    @abstractmethod
    def open_url(self, url: str) -> None:
        """Open a URL in the default browser."""
        ...

    @abstractmethod
    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification."""
        ...

    def secure_storage_available(self) -> bool:
        """Check if hardware-backed secure storage is available."""
        return False
