# Building PWM for All Platforms

## Quick Start

| Platform | Command | Output |
|----------|---------|--------|
| CLI (all) | `pip install -e .` | `pwm` command |
| GUI (desktop) | `pip install -e ".[gui]" && pwm-gui` | Kivy window |
| Windows .exe | `pyinstaller pyinstaller.spec` | `dist/PWM.exe` |
| macOS .app | `pyinstaller pyinstaller.spec` | `dist/PWM.app` |
| Android .apk | `buildozer android debug` | `bin/*.apk` |
| iOS .ipa | `./kivy-ios.sh` | Xcode project |

## Desktop — Standalone Executable

```bash
pip install pyinstaller kivy cryptography
pyinstaller pyinstaller.spec
```

The output is `dist/PWM` (or `dist/PWM.exe` on Windows).

## Android — APK

```bash
# Ubuntu 22.04+ / WSL2
pip install buildozer cython
buildozer init       # (only first time, already done)
buildozer android debug
```

**Requirements:**
- Linux (Ubuntu 22.04 recommended)
- OpenJDK 17: `sudo apt install openjdk-17-jdk`
- Android SDK/NDK (auto-downloaded by Buildozer)
- 4GB+ RAM free

## iOS — IPA (macOS only)

```bash
pip install kivy-ios
./kivy-ios.sh
```

Then open the Xcode project in `.kivy-ios/PWM/`.

## Architecture

```
┌─────────────────────────────────────────┐
│              app/ (Kivy GUI)            │  ← Shared UI
│   main.py, kv/pwm.kv, screens/         │
├─────────────────────────────────────────┤
│           platform/ (Abstraction)       │  ← Per-platform
│   base.py, desktop.py, android.py      │
├─────────────────────────────────────────┤
│           pwm/core (Logic)              │  ← Shared core
│   crypto.py, vault.py, models.py       │
├─────────────────────────────────────────┤
│           pwm/cli (CLI)                 │  ← Terminal interface
│           pwm/utils                     │
└─────────────────────────────────────────┘
```
