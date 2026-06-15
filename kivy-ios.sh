#!/bin/bash
# Build PWM for iOS using kivy-ios toolchain
# Requirements: macOS with Xcode, kivy-ios installed
#
# Usage:
#   chmod +x kivy-ios.sh
#   ./kivy-ios.sh

set -e

APP_NAME="PWM"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="${PROJECT_DIR}/.kivy-ios"

echo "=== PWM iOS Build Script ==="
echo ""

# Check environment
if [[ "$(uname)" != "Darwin" ]]; then
    echo "ERROR: iOS builds require macOS with Xcode."
    exit 1
fi

if ! command -v toolchain &> /dev/null; then
    echo "Installing kivy-ios toolchain..."
    pip install kivy-ios
fi

# Build recipes
echo ""
echo "Step 1/4: Building Python + dependencies..."
toolchain build python3 kivy cryptography

# Create Xcode project
echo ""
echo "Step 2/4: Creating Xcode project..."
toolchain create "${APP_NAME}" "${PROJECT_DIR}"

# Copy app files
echo ""
echo "Step 3/4: Copying app files..."
cp "${PROJECT_DIR}/run_gui.py" "${BUILD_DIR}/${APP_NAME}/main.py"
cp -r "${PROJECT_DIR}/app" "${BUILD_DIR}/${APP_NAME}/app"
cp -r "${PROJECT_DIR}/pwm" "${BUILD_DIR}/${APP_NAME}/pwm"
cp -r "${PROJECT_DIR}/platform" "${BUILD_DIR}/${APP_NAME}/platform"

# Update Xcode project settings
echo ""
echo "Step 4/4: Configuring Xcode project..."

# Set bundle identifier
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier org.pwm.app" \
    "${BUILD_DIR}/${APP_NAME}/${APP_NAME}-Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName PWM" \
    "${BUILD_DIR}/${APP_NAME}/${APP_NAME}-Info.plist" 2>/dev/null || true

echo ""
echo "=== Done! ==="
echo "Xcode project created at: ${BUILD_DIR}/${APP_NAME}/"
echo ""
echo "To build and deploy to a device:"
echo "  1. Open ${BUILD_DIR}/${APP_NAME}/${APP_NAME}.xcodeproj in Xcode"
echo "  2. Select your signing team"
echo "  3. Build to device or Archive for App Store"
