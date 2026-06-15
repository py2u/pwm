# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for PWM — standalone desktop executable."""

import sys
from pathlib import Path

block_cipher = None

# Collect platform-dependent assets
datas = [
    ("app/kv/pwm.kv", "app/kv"),
]
hiddenimports = [
    "pwm", "pwm.core", "pwm.cli", "pwm.utils",
    "pwm_platform", "pwm_platform.desktop",
    "cryptography", "cryptography.hazmat.backends.openssl",
    "kivy", "kivy.uix.screenmanager",
]

a = Analysis(
    ["run_gui.py"],
    pathex=[str(Path(__file__).parent)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "unittest", "email", "http",
        "xml", "pydoc", "test", "distutils",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PWM",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico path here for Windows
)

# Platform-specific
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="PWM.app",
        icon=None,  # Add .icns path here for macOS
        bundle_identifier="org.pwm.app",
        info_plist={
            "CFBundleName": "PWM Password Manager",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
