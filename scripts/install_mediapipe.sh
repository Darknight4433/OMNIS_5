#!/bin/bash

echo "========================================"
echo "OMNIS MediaPipe Installer for Raspberry Pi"
echo "========================================"
echo "This script attempts to install MediaPipe for gesture recognition."
echo "Note: This can be difficult on 32-bit Raspberry Pi OS."
echo.

# Check Python version
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Detected Python Version: $PY_VERSION"

echo "Step 1: Updating pip..."
python3 -m pip install --upgrade pip

echo "Step 2: Trying standard installation (Works on 64-bit OS)..."
python3 -m pip install mediapipe
if [ $? -eq 0 ]; then
    echo "✅ Success! mediapipe installed."
    exit 0
fi

echo "⚠️ Standard install failed. Trying 'mediapipe-rpi4' (Community Build)..."
python3 -m pip install mediapipe-rpi4
if [ $? -eq 0 ]; then
    echo "✅ Success! mediapipe-rpi4 installed."
    exit 0
fi

echo "⚠️ trying 'mediapipe-rpi3'..."
python3 -m pip install mediapipe-rpi3
if [ $? -eq 0 ]; then
    echo "✅ Success! mediapipe-rpi3 installed."
    exit 0
fi

echo "Step 3: Trying older compatible versions..."
# Often newer versions don't have wheels for armv7l
python3 -m pip install mediapipe==0.8.11
if [ $? -eq 0 ]; then
    echo "✅ Success! Older mediapipe installed."
    exit 0
fi

echo "========================================"
echo "❌ FAILED: Could not install mediapipe automatically."
echo "You might be running a 32-bit OS where support is limited."
echo "Suggestions:"
echo "1. Re-image your Pi with 'Raspberry Pi OS (64-bit)'."
echo "2. Or ignore this (Gestures will just be disabled)."
echo "========================================"
exit 1
