#!/bin/bash
# Setup script for OMNIS on Raspberry Pi
# Run this once to install all dependencies

echo "========================================"
echo "OMNIS Setup for Raspberry Pi"
echo "========================================"
echo ""

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-dev portaudio19-dev python3-pyaudio

# Install Python packages
echo ""
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install opencv-python face-recognition SpeechRecognition gtts pygame cvzone google-generativeai numpy

# Install additional audio dependencies
echo ""
echo "Installing additional audio dependencies..."
sudo apt-get install -y alsa-utils pulseaudio

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Put face photos (JPG) in the 'images/faces/' folder"
echo "2. Run: python3 EncodeGenerator.py"
echo "3. Copy secrets_local.py.example to secrets_local.py"
echo "4. Edit secrets_local.py and add your Gemini API key"
echo "5. Run: python3 main.py"
echo ""
echo "Your API key is already in secrets_local.py if you copied the folder!"
echo ""
