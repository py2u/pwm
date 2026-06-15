[app]
# Application name
title = PWM Password Manager

# Package name (unique on Google Play)
package.name = pwm
package.domain = org.pwm

# Source directory
source.dir = .

# Main entry point
main.py = run_gui.py

# Application version
version = 1.0.0

# Requirements
requirements = python3,kivy>=2.2.0,cryptography>=41.0.0,plyer

# Permissions
android.permissions = INTERNET

# Android API level
android.api = 33
android.minapi = 26
android.ndk = 25b

# Architecture
android.arch = arm64-v8a

# Gradle dependencies (for AndroidX)
android.gradle_dependencies = androidx.core:core:1.12.0

# Java source for Android platform
android.add_src = platform/android_java

# Services — auto-start not needed for password manager
# services = ...

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Icon (optional)
# icon.filename = %(source.dir)s/assets/icon.png

# Presplash
# presplash.filename = %(source.dir)s/assets/presplash.png

# Log level
log_level = 2

# Debug mode (set to 0 for release)
debug = 0

# Copy APK after build
android.allow_download_cache = 1

[buildozer]
# Build directory
build_dir = .buildozer

# Log level
log_level = 2

# Warn on permissions
warn_on_root = 1
