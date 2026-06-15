#!/usr/bin/env python3
"""PWM GUI launcher — cross-platform (Desktop + Mobile).

Usage:
    python run_gui.py              # Launch the Kivy GUI
    pwm-gui                        # If installed via pip with [gui] extras

Build instructions per platform:
    Desktop (exe/app):
        pip install pyinstaller
        pyinstaller pyinstaller.spec
        # → dist/PWM.exe (Windows) or dist/PWM.app (macOS)

    Android (apk):
        pip install buildozer
        buildozer android debug
        # → bin/*.apk

    iOS (ipa):
        # macOS + Xcode required
        ./kivy-ios.sh
"""

import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Launch the PWM GUI application."""
    try:
        from kivy import require
        require("2.0.0")
    except ImportError:
        print(
            "ERROR: Kivy is required for the GUI.\n"
            "Install it with: pip install kivy\n"
            "Or use the CLI instead: pwm --help"
        )
        sys.exit(1)

    from app.main import PwmApp
    PwmApp().run()


if __name__ == "__main__":
    main()
